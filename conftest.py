"""
Pytest configuration for SkyElectric mobile UI tests.

State machine before each test:
  - login_screen_driver  → force-restarts app → guarantees login screen (for negative tests)
  - logged_in_driver     → detects state → OTP login / PIN unlock / power screen pass-through
"""

import os
import time
import subprocess
from datetime import datetime
from enum import Enum, auto
from typing import Optional

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

from pages.login_page import LoginPage
from pages.navigation_page import NavigationPage
from utils.gmail_helper import get_otp_from_gmail
from config import APP_ACTIVITY, APP_PACKAGE

# ── constants ─────────────────────────────────────────────────────────────────

ADB      = "/home/fatima/android-sdk/platform-tools/adb"
APK_PATH = os.path.join(os.path.dirname(__file__), "app-skyelectric-production.apk")

TEST_EMAIL = "fatimanoor@skyelectric.com"

APP_READY_WAIT   = 6   # seconds after launching the app before reading page source
STATE_SETTLE_WAIT = 3  # seconds between state checks when verifying


# ── app state enum ────────────────────────────────────────────────────────────

class AppState(Enum):
    LOGIN  = auto()   # email / OTP entry screen
    PIN    = auto()   # security lock / biometric prompt
    POWER  = auto()   # main Power Distribution screen (logged in)
    UNKNOWN = auto()  # anything else — transient / loading / crash


# ── low-level helpers ─────────────────────────────────────────────────────────

def _adb(*args):
    """Run an adb shell command, ignoring errors."""
    subprocess.run([ADB, *args], check=False)


def _force_start(package: str, activity: str) -> None:
    _adb("shell", "am", "force-stop", package)
    time.sleep(2)
    _adb("shell", "am", "start", "-n", f"{package}/{activity}")
    time.sleep(APP_READY_WAIT)


def restart_app(driver) -> None:
    """Terminate and relaunch the app through Appium; fall back to adb."""
    try:
        driver.terminate_app(APP_PACKAGE)
        time.sleep(2)
        driver.activate_app(APP_PACKAGE)
        time.sleep(APP_READY_WAIT)
    except Exception:
        _force_start(APP_PACKAGE, APP_ACTIVITY)


# ── state detection ───────────────────────────────────────────────────────────

def detect_state(driver) -> AppState:
    """
    Read the current page source and return the matching AppState.

    Waits STATE_SETTLE_WAIT seconds before reading so transient loading
    screens don't produce a false 'login' detection.
    """
    time.sleep(STATE_SETTLE_WAIT)
    source = driver.page_source.lower()

    if "power" in source and "distribution" in source:
        return AppState.POWER

    if "lockpassword" in source or "authentication required" in source:
        return AppState.PIN

    # Confirm LOGIN button is still present after a brief extra pause
    # (guards against catching it during a startup transition).
    if driver.find_elements(*LoginPage.LOGIN_BUTTON):
        time.sleep(2)
        if driver.find_elements(*LoginPage.LOGIN_BUTTON):
            return AppState.LOGIN

    return AppState.UNKNOWN


# ── OTP fetcher ───────────────────────────────────────────────────────────────

def _fetch_otp(since_timestamp=None) -> Optional[str]:
    return get_otp_from_gmail(
        sender_filter="skyelectric",
        subject_filter="OTP",
        wait_seconds=90,
        since_timestamp=since_timestamp,
    )


# ── state handlers ────────────────────────────────────────────────────────────

def _handle_login(driver) -> None:
    """Perform a full OTP login from the login screen."""
    print("[APP] Login screen detected → performing OTP login")
    login = LoginPage(driver)
    login.login_with_otp(email=TEST_EMAIL, otp_fetcher_func=_fetch_otp)
    login.handle_pin_if_present()
    time.sleep(5)


def _handle_pin(driver) -> None:
    """Dismiss the security lock and verify we reach the power screen."""
    print("[APP] Security lock detected → entering PIN")
    login = LoginPage(driver)
    login.handle_pin_if_present()
    time.sleep(STATE_SETTLE_WAIT)


def _handle_power(driver) -> None:
    """Already on the power screen — optionally dismiss any lingering PIN overlay."""
    print("[APP] Already on Power Distribution screen")
    LoginPage(driver).handle_pin_if_present()


# ── public state-machine entry points ─────────────────────────────────────────

def ensure_app_ready(driver, _attempt: int = 0) -> None:
    """
    Guarantee the app is on the Power Distribution screen.

    Detects the current state and takes the appropriate action:
      POWER   → done (optionally clears PIN overlay)
      PIN     → unlock, then verify we reach POWER
      LOGIN   → full OTP flow, then handle any PIN overlay
      UNKNOWN → restart app and retry (max 2 times)

    Raises RuntimeError after 2 failed restart attempts.
    """
    if _attempt > 2:
        raise RuntimeError(
            "[APP] Could not reach Power Distribution screen after 2 restarts."
        )

    state = detect_state(driver)
    print(f"\n[APP] State detected: {state.name!r}  (attempt {_attempt + 1})")

    if state is AppState.POWER:
        _handle_power(driver)
        return

    if state is AppState.PIN:
        _handle_pin(driver)
        # Verify we actually reached POWER after unlocking
        if detect_state(driver) is not AppState.POWER:
            ensure_app_ready(driver, _attempt + 1)
        return

    if state is AppState.LOGIN:
        _handle_login(driver)
        return

    # UNKNOWN — restart and recurse
    print("[APP] Unknown state → restarting app")
    restart_app(driver)
    ensure_app_ready(driver, _attempt + 1)


def ensure_login_screen(driver) -> None:
    """
    Guarantee the app is on the Login screen.

    Used exclusively by login-negative tests (invalid email, empty email, …).
    Always restarts the app so we start from a clean, unauthenticated state.
    """
    print("\n[APP] Restarting app to guarantee clean login screen")
    restart_app(driver)

    state = detect_state(driver)
    print(f"[APP] Post-restart state: {state.name!r}")

    if state is AppState.LOGIN:
        print("[APP] Login screen confirmed — ready for negative test")
        return

    if state is AppState.PIN:
        # Edge case: app restarted but went straight to PIN
        # Dismiss PIN first, log out, then the login screen should appear.
        print("[APP] PIN appeared after restart — dismissing then logging out")
        _handle_pin(driver)
        time.sleep(2)
        # Attempt log-out via the app's navigation; fall back to a second restart.
        try:
            nav = NavigationPage(driver)
            nav.logout()
            time.sleep(STATE_SETTLE_WAIT)
        except Exception:
            restart_app(driver)

        if detect_state(driver) is not AppState.LOGIN:
            raise RuntimeError(
                "[APP] Could not reach Login screen for negative test after logout attempt."
            )
        return

    raise RuntimeError(
        f"[APP] Unexpected state '{state.name}' after restart — "
        "cannot guarantee Login screen for negative test."
    )


# ── pytest hooks ───────────────────────────────────────────────────────────────

def pytest_configure(config):
    os.makedirs("reports/screenshots", exist_ok=True)
    for mark in ("smoke", "regression", "ui", "functional"):
        config.addinivalue_line("markers", mark)


def pytest_collection_modifyitems(items):
    """Run login-negative tests first so they run before any session login."""
    LOGIN_NEGATIVE = {
        "test_invalid_email_shows_error",
        "test_empty_email_shows_error",
    }
    PRIORITY = {
        "test_invalid_email_shows_error": 0,
        "test_empty_email_shows_error":   1,
        "test_full_login_flow":           2,
    }
    items.sort(key=lambda i: PRIORITY.get(i.name, 99))


def pytest_addoption(parser):
    parser.addoption("--device-name",   default="Android Device")
    parser.addoption("--appium-server", default="http://127.0.0.1:4723")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            try:
                screenshot_dir = "reports/screenshots"
                os.makedirs(screenshot_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(screenshot_dir, f"{item.name}_{timestamp}.png")

                if driver.session_id:
                    driver.save_screenshot(path)
                    print(f"\n📸 Screenshot saved: {path}")
                else:
                    print("\n⚠️  Driver session already dead — skipping screenshot")
            except Exception as e:
                print(f"\n❌ Screenshot skipped: {e}")


# ── session-scoped fixtures ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def device_name(request):
    return request.config.getoption("--device-name")


@pytest.fixture(scope="session")
def appium_server(request):
    return request.config.getoption("--appium-server")


@pytest.fixture(scope="session")
def driver(appium_server, device_name):
    """
    Single Appium session shared across all tests.
    No automatic app-state handling here — each test fixture decides
    what state it needs.
    """
    options = UiAutomator2Options()
    options.platform_name          = "Android"
    options.device_name            = device_name
    options.app                    = APK_PATH
    options.app_package            = APP_PACKAGE
    options.app_activity           = APP_ACTIVITY
    options.no_reset               = True
    options.auto_grant_permissions = True
    options.new_command_timeout    = 300

    options.set_capability("uiautomator2ServerLaunchTimeout", 60000)
    options.set_capability("adbExecTimeout", 60000)

    drv = webdriver.Remote(command_executor=appium_server, options=options)
    drv.implicitly_wait(12)
    time.sleep(APP_READY_WAIT)

    yield drv
    drv.quit()


# ── function-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="function")
def navigation_page(driver):
    """Provides a NavigationPage instance. Assumes the app is already logged in."""
    return NavigationPage(driver)


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """
    Use this for: navigation tests, battery screen tests, power distribution
    tests — anything that requires the app to be on the Power Distribution screen.

    Detects the current state and takes the minimum action needed:
      - Already on power screen → nothing to do
      - Security lock present  → enters PIN
      - On login screen        → performs full OTP login
      - Unknown state          → restarts app and retries
    """
    ensure_app_ready(driver)
    return driver


@pytest.fixture(scope="function")
def login_screen_driver(driver):
    """
    Use this for: login negative tests (invalid email, empty email, etc.)

    Always restarts the app to guarantee a fresh, unauthenticated login screen.
    Never attempts to log in.
    """
    ensure_login_screen(driver)
    return driver