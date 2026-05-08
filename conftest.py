"""
Pytest configuration for SkyElectric mobile UI tests.

State machine before each test:
  - login_screen_driver  → force-restarts app → guarantees login screen (for negative tests)
  - logged_in_driver     → detects state → OTP login / PIN unlock / power screen pass-through

Error reporting:
  - pytest_runtest_makereport      → saves screenshot + rewrites cryptic Selenium errors
                                     into plain English for both terminal and HTML report
  - pytest_html_results_table_html → injects friendly failure card + inline screenshot
                                     into the HTML report row
"""

import os
import re
import base64
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

# ── constants ──────────────────────────────────────────────────────────────────

ADB      = "/home/fatima/android-sdk/platform-tools/adb"
APK_PATH = os.path.join(os.path.dirname(__file__), "app-skyelectric-production.apk")

TEST_EMAIL = "fatimanoor@skyelectric.com"

APP_READY_WAIT    = 6   # seconds after launching the app before reading page source
STATE_SETTLE_WAIT = 3   # seconds between state checks when verifying
SHORT_WAIT        = 2   # seconds — brief stabilisation pause between quick steps
DOUBLE_CHECK_WAIT = 1   # seconds — reduced pause for login-button double-check in detect_state

# Strings that identify the Android security / biometric lock screen.
# Add more entries here if your device shows different text.
_PIN_SCREEN_SIGNALS = (
    "lockpassword",
    "authentication required",
    "enter your pin",
    "enter pin",
    "confirm your pin",
    "biometric",
    "fingerprint",
    "use pin instead",
    "security lock",
)


# ── app state enum ─────────────────────────────────────────────────────────────

class AppState(Enum):
    LOGIN   = auto()   # email / OTP entry screen
    PIN     = auto()   # security lock / biometric prompt
    POWER   = auto()   # main Power Distribution screen (logged in)
    UNKNOWN = auto()   # anything else — transient / loading / crash


# ── low-level helpers ──────────────────────────────────────────────────────────

def _adb(*args):
    """Run an adb shell command, ignoring errors."""
    subprocess.run([ADB, *args], check=False)


def _force_start(package: str, activity: str) -> None:
    _adb("shell", "am", "force-stop", package)
    time.sleep(SHORT_WAIT)
    _adb("shell", "am", "start", "-n", f"{package}/{activity}")
    time.sleep(APP_READY_WAIT)


def restart_app(driver) -> None:
    """
    Terminate and relaunch the app through Appium; fall back to adb if Appium fails.

    After the adb fallback, driver.activate_app() is called so Appium
    re-attaches to the running process — otherwise subsequent page_source
    calls may fail or return stale data.
    """
    try:
        driver.terminate_app(APP_PACKAGE)
        time.sleep(SHORT_WAIT)
        driver.activate_app(APP_PACKAGE)
        time.sleep(APP_READY_WAIT)
    except Exception:
        _force_start(APP_PACKAGE, APP_ACTIVITY)
        # Re-attach Appium so it tracks the newly started process.
        try:
            driver.activate_app(APP_PACKAGE)
        except Exception:
            pass  # best-effort; the app is running via adb anyway


# ── state detection ────────────────────────────────────────────────────────────

def detect_state(driver) -> AppState:
    """
    Read the current page source and return the matching AppState.

    Waits STATE_SETTLE_WAIT seconds before reading so transient loading
    screens don't produce a false detection.

    Detection order matters:
      1. POWER  — most specific (two required keywords)
      2. PIN    — broad set of lock-screen signals (see _PIN_SCREEN_SIGNALS)
      3. LOGIN  — confirmed by element presence with a reduced double-check pause
      4. UNKNOWN — fallback
    """
    time.sleep(STATE_SETTLE_WAIT)
    # source = driver.page_source.lower()
    try:
        source = driver.page_source.lower()
    except Exception as e:
        print(f"[detect_state] page_source failed — instrumentation likely crashed: {e}")
        return AppState.UNKNOWN



    # ── 1. Power Distribution screen ──────────────────────────────────────────
    if "power" in source and "distribution" in source:
        return AppState.POWER

    # ── 2. Security / biometric lock screen ───────────────────────────────────
    if any(signal in source for signal in _PIN_SCREEN_SIGNALS):
        return AppState.PIN

    # Element-based fallback for PIN (handles cases where text is not in source)
    try:
        pin_elements = (
            driver.find_elements("xpath", '//*[contains(@resource-id, "lockPassword")]')
            or driver.find_elements("xpath", '//*[contains(@resource-id, "pinEntry")]')
            or driver.find_elements("xpath", '//*[contains(@resource-id, "biometric")]')
        )
        if pin_elements:
            return AppState.PIN
    except Exception:
        pass  # element search is best-effort

    # ── 3. Login screen ───────────────────────────────────────────────────────
    if driver.find_elements(*LoginPage.LOGIN_BUTTON):
        time.sleep(DOUBLE_CHECK_WAIT)
        if driver.find_elements(*LoginPage.LOGIN_BUTTON):
            return AppState.LOGIN

    return AppState.UNKNOWN


# ── OTP fetcher ────────────────────────────────────────────────────────────────

def _fetch_otp(since_timestamp=None) -> Optional[str]:
    """
    Thin wrapper around get_otp_from_gmail with project-specific defaults.
    """
    return get_otp_from_gmail(
        sender_filter="skyelectric",
        subject_filter="OTP",
        wait_seconds=90,
        since_timestamp=since_timestamp,
    )


# ── state handlers ─────────────────────────────────────────────────────────────

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

    try:
        source = driver.page_source.lower()

        if "power" in source and "distribution" in source:
            print("[APP] PIN dismissed — Power screen confirmed")
            return

        print("[APP] Power screen not yet visible after PIN")

    except Exception as e:
        print(f"[APP] page_source failed after PIN entry: {e}")

    print("[APP] PIN dismissal did not reach Power screen — will retry from ensure_app_ready")
   

def _handle_power(driver) -> None:
    """Already on the power screen — optionally dismiss any lingering PIN overlay."""
    print("[APP] Already on Power Distribution screen")
    LoginPage(driver).handle_pin_if_present()

def _restart_uiautomator2(driver) -> bool:
    """Force-kill and restart the UiAutomator2 server process on the device."""
    print("[RECOVERY] Attempting UiAutomator2 server restart via adb...")
    try:
        _adb("shell", "am", "force-stop", "io.appium.uiautomator2.server")
        _adb("shell", "am", "force-stop", "io.appium.uiautomator2.server.test")
        time.sleep(SHORT_WAIT)
        _force_start(APP_PACKAGE, APP_ACTIVITY)
        try:
            driver.activate_app(APP_PACKAGE)
            time.sleep(APP_READY_WAIT)
        except Exception:
            pass
        print("[RECOVERY] UiAutomator2 restart complete")
        return True
    except Exception as e:
        print(f"[RECOVERY] Failed: {e}")
        return False
# ── public state-machine entry points ─────────────────────────────────────────

def ensure_app_ready(driver, _attempt: int = 0) -> None:
    """
    Guarantee the app is on the Power Distribution screen.

    Detects the current state and takes the appropriate action:
      POWER   → done (optionally clears PIN overlay)
      PIN     → unlock, then verify we reach POWER
      LOGIN   → full OTP flow, then verify we reach POWER
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
        post_state = detect_state(driver)
        print(f"[APP] Post-PIN state: {post_state.name!r}")
        if post_state is not AppState.POWER:
            ensure_app_ready(driver, _attempt + 1)
        return

    if state is AppState.LOGIN:
        _handle_login(driver)
        post_state = detect_state(driver)
        print(f"[APP] Post-login state: {post_state.name!r}")
        if post_state is not AppState.POWER:
            print("[APP] Login did not reach Power screen — retrying")
            ensure_app_ready(driver, _attempt + 1)
        return

    # UNKNOWN — try UiAutomator2 recovery first, then full restart
    print("[APP] Unknown state → attempting UiAutomator2 recovery")
    recovered = _restart_uiautomator2(driver)
    if not recovered:
        print("[APP] Recovery failed → falling back to full app restart")
        restart_app(driver)
    ensure_app_ready(driver, _attempt + 1)


def ensure_login_screen(driver, _attempt: int = 0) -> None:
    """
    Guarantee the app is on the Login screen.

    Used exclusively by login-negative tests (invalid email, empty email, ...).
    Always restarts the app so we start from a clean, unauthenticated state.

    Retries up to 2 times before raising.
    """
    if _attempt > 2:
        raise RuntimeError(
            "[APP] Could not reach Login screen for negative test after 2 attempts."
        )

    print(f"\n[APP] Restarting app to guarantee clean login screen (attempt {_attempt + 1})")
    restart_app(driver)

    state = detect_state(driver)
    print(f"[APP] Post-restart state: {state.name!r}")

    if state is AppState.LOGIN:
        print("[APP] Login screen confirmed — ready for negative test")
        return

    if state is AppState.PIN:
        print("[APP] PIN appeared after restart — dismissing then logging out")
        _handle_pin(driver)
        time.sleep(SHORT_WAIT)
        try:
            nav = NavigationPage(driver)
            nav.logout()
            time.sleep(STATE_SETTLE_WAIT)
        except Exception:
            pass  # logout failed — fall through to retry

        ensure_login_screen(driver, _attempt + 1)
        return

    # Any other unexpected state — retry from the top.
    print(f"[APP] Unexpected state '{state.name}' after restart — retrying")
    ensure_login_screen(driver, _attempt + 1)


# ══════════════════════════════════════════════════════════════════════════════
# ERROR REPORTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _plain_english(longrepr_text: str) -> dict:
    """
    Convert a raw pytest/Selenium failure string into a short, human-readable
    dict with keys 'reason' and 'detail'.

    Handles every failure pattern seen in this test suite:
      1. NoSuchElementError / TimeoutException  → element not found
      2. TimeoutException (general)             → screen did not load in time
      3. AssertionError with value mismatch     → wrong value on screen
      4. AssertionError with count mismatch     → wrong number of elements
      5. AssertionError with label/text check   → text not visible on screen
      6. Generic AssertionError                 → catch-all with message
      7. Everything else                        → last-line fallback
    """
    t = longrepr_text

    # ── 1. Element not found ──────────────────────────────────────────────────
    if "NoSuchElementError" in t or (
        "TimeoutException" in t and "could not be located" in t
    ):
        locator_hint = ""
        m = re.search(r'self\.([\w_]+)\b', t)
        if m:
            locator_hint = f" (looking for: {m.group(1)})"
        return {
            "reason": "UI element not found on screen",
            "detail": (
                f"The test tried to find a UI element{locator_hint} "
                "but it was not visible. Likely causes: the screen needs "
                "to be scrolled down first, the element label changed in a "
                "new build, or the screen did not finish loading."
            ),
        }

    # ── 2. General timeout ────────────────────────────────────────────────────
    if "TimeoutException" in t:
        return {
            "reason": "Timed out waiting for the screen to load",
            "detail": (
                "The test waited too long for something to appear and gave up. "
                "The app may be slow, the expected screen may not have opened, "
                "or a network call is taking too long."
            ),
        }

    # ── 3. Assertion: value mismatch (e.g. 'false' == 'true') ─────────────────
    eq = re.search(r"assert\s+'(.+?)'\s+==\s+'(.+?)'", t)
    if eq:
        got, expected = eq.group(1), eq.group(2)
        return {
            "reason": f"Wrong value — expected '{expected}', got '{got}'",
            "detail": (
                f"The test read a value from the screen and it did not match. "
                f"Expected: '{expected}'.  Actual: '{got}'. "
                "This usually means the wrong tab is selected, a toggle did not "
                "change state, or the app launched on a different screen."
            ),
        }

    # ── 4. Assertion: element count mismatch ──────────────────────────────────
    cnt = re.search(r"Expected (\d+) .+?, found (\d+)", t)
    if cnt:
        exp_n, got_n = cnt.group(1), cnt.group(2)
        return {
            "reason": f"Wrong number of items — expected {exp_n}, found {got_n}",
            "detail": (
                f"The test counted visible elements and found {got_n} instead of "
                f"{exp_n}. The graph may not have fully rendered, the screen may "
                "need to be scrolled, or the data is empty for today."
            ),
        }

    # ── 5. Assertion: label / text not visible ────────────────────────────────
    lbl = re.search(
        r"AssertionError:\s*['\"]?(.+?)['\"]?\s*(label|header|not found|not visible)",
        t, re.IGNORECASE
    )
    if lbl:
        label = lbl.group(1).strip("'\" ")
        return {
            "reason": f"Expected text not visible: '{label}'",
            "detail": (
                f"The test expected to see '{label}' on screen but could not find it. "
                "The element may be hidden, off-screen, or have a different label "
                "in the current app version."
            ),
        }

    # ── 6. Generic AssertionError ─────────────────────────────────────────────
    if "AssertionError" in t:
        msg = ""
        for line in t.splitlines():
            line = line.strip()
            if line.startswith("AssertionError:"):
                msg = line.replace("AssertionError:", "").strip()
                break
        return {
            "reason": "A test check failed",
            "detail": msg or "One of the test assertions did not pass. Check the test name for context.",
        }

    # ── 7. Catch-all ──────────────────────────────────────────────────────────
    last_line = t.strip().splitlines()[-1] if t.strip() else ""
    return {
        "reason": "Unexpected error during test",
        "detail": last_line or "An unknown error occurred.",
    }


def _find_screenshot_for(test_name: str) -> Optional[str]:
    """Return the path to the most recent screenshot for test_name, or None."""
    screenshots_dir = os.path.join("reports", "screenshots")
    if not os.path.isdir(screenshots_dir):
        return None
    core = re.sub(r"\[.*?\]", "", test_name)   # strip parametrize brackets
    candidates = [
        f for f in os.listdir(screenshots_dir)
        if core in f and f.endswith(".png")
    ]
    if not candidates:
        return None
    candidates.sort(reverse=True)              # most recent first (timestamp in name)
    return os.path.join(screenshots_dir, candidates[0])


def _encode_image(path: str) -> str:
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# PYTEST HOOKS
# ══════════════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    os.makedirs("reports/screenshots", exist_ok=True)
    for mark in ("smoke", "regression", "ui", "functional"):
        config.addinivalue_line("markers", mark)


def pytest_collection_modifyitems(items):
    """
    Two-level sort:
      1. Primary   → module file order (login → power dist → navigation → …)
      2. Secondary → within test_login.py, keep negative tests before the full flow
    """
    MODULE_ORDER = [
        "test_login",
        "test_power_distribution",
        "test_navigation",
        "test_solar_production",
        "test_grid_interaction",
        "test_battery_management",
        "test_menu_option",
        "test_logout",
    ]

    # Within test_login.py — negative tests must run before the OTP login flow
    LOGIN_PRIORITY = {
        "test_invalid_email_shows_error": 0,
        "test_empty_email_shows_error":   1,
        "test_full_login_flow":           2,
    }

    def sort_key(item):
        module_name = item.module.__name__.split(".")[-1]  # e.g. "test_login"
        module_rank = (
            MODULE_ORDER.index(module_name)
            if module_name in MODULE_ORDER
            else len(MODULE_ORDER)   # unknown modules run last
        )
        test_rank = LOGIN_PRIORITY.get(item.name, 99)
        return (module_rank, test_rank)

    items.sort(key=sort_key)


def pytest_addoption(parser):
    parser.addoption("--device-name",   default="Android Device")
    parser.addoption("--appium-server", default="http://127.0.0.1:4723")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    # ── 1. Save screenshot ────────────────────────────────────────────────────
    screenshot_path = None
    driver = item.funcargs.get("driver")
    if driver:
        try:
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(screenshot_dir, f"{item.name}_{timestamp}.png")
            if driver.session_id:
                driver.save_screenshot(path)
                screenshot_path = path
                print(f"\n📸 Screenshot saved: {path}")
            else:
                print("\n⚠️  Driver session already dead — skipping screenshot")
        except Exception as e:
            print(f"\n❌ Screenshot skipped: {e}")

    # ── 2. Build plain-English summary ────────────────────────────────────────
    longrepr_text = (
        report.longreprtext
        if hasattr(report, "longreprtext")
        else str(report.longrepr)
    )
    plain = _plain_english(longrepr_text)

    # Stash on report so the HTML hook can read it
    report._plain = plain
    report._shot  = screenshot_path or _find_screenshot_for(item.name)

    # ── 3. Rewrite terminal output ────────────────────────────────────────────
    friendly_terminal = (
        f"\n{'─' * 62}\n"
        f"  ✗  WHAT WENT WRONG:  {plain['reason']}\n"
        f"     {plain['detail']}\n"
        f"{'─' * 62}"
    )
    if hasattr(report.longrepr, "reprcrash"):
        original_msg = report.longrepr.reprcrash.message
        report.longrepr.reprcrash.message = (
            friendly_terminal
            + f"\n\n  Technical detail:\n  {original_msg}"
        )


def pytest_html_results_table_html(report, data):
    """
    Inject a friendly amber failure card + inline screenshot into the
    HTML report row for every failed test.

    Inserted at position 0 so it appears above the raw traceback.
    """
    if not (hasattr(report, "_plain") and report.failed):
        return

    plain = report._plain

    # Build screenshot block if available
    screenshot_block = ""
    if getattr(report, "_shot", None):
        try:
            b64 = _encode_image(report._shot)
            screenshot_block = f"""
            <div style="margin-top:14px;">
              <p style="font-weight:600;margin:0 0 6px;color:#374151;font-size:12px;">
                📸 Screenshot at point of failure
              </p>
              <img src="data:image/png;base64,{b64}"
                   style="max-width:100%;border:1px solid #d1d5db;
                          border-radius:6px;display:block;" />
            </div>"""
        except Exception:
            pass

    card = f"""
    <div style="
        background : #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding    : 14px 16px;
        margin     : 6px 0 10px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size  : 13px;
        line-height: 1.65;
    ">
      <p style="margin:0 0 5px;font-weight:700;color:#92400e;font-size:14px;">
        ⚠&nbsp; {plain['reason']}
      </p>
      <p style="margin:0;color:#78350f;">
        {plain['detail']}
      </p>
      {screenshot_block}
    </div>
    """

    data.insert(0, card)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION-SCOPED FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

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
    yield drv
    try:
        if drv.session_id:
            drv.quit()
    except Exception as e:
        print(f"\n[TEARDOWN] driver.quit() skipped — session already dead: {e}")


# ── function-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """
    Use this for: navigation tests, battery screen tests, power distribution
    tests — anything that requires the app to be on the Power Distribution screen.
    """
    ensure_app_ready(driver)
    return driver


@pytest.fixture(scope="function")
def navigation_page(logged_in_driver):
    """
    Provides a NavigationPage instance guaranteed to be on the Power
    Distribution screen.

    Depends on logged_in_driver (rather than the raw driver) so that tests
    using only navigation_page do not silently run against an unauthenticated app.
    """
    return NavigationPage(logged_in_driver)




@pytest.fixture(scope="function")
def login_screen_driver(driver):
    """
    Use this for: login negative tests (invalid email, empty email, etc.)

    Always restarts the app to guarantee a fresh, unauthenticated login screen.
    Never attempts to log in.
    """
    ensure_login_screen(driver)
    return driver


