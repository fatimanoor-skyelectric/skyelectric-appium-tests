import time
import pytest
from pages.login_page import LoginPage
from config import APP_PACKAGE

TEST_EMAIL = "fatimanoor@skyelectric.com"
TEST_PIN   = "1111"


class TestLoginFlow:

    # ─────────────────────────────────────────────────────────────────
    # TC-NEG-01 │ Invalid email format
    # Must run BEFORE full login (still on login screen)
    # ─────────────────────────────────────────────────────────────────
    def test_invalid_email_shows_error(self, driver):
        """
        GIVEN user is on login screen
        WHEN  they enter 'notanemail' and tap Login
        THEN  an inline error appears containing 'invalid email'
        """
        login = LoginPage(driver)
        print("\n[TC-NEG-01] Invalid email format test")

        login.wait_for_login_screen()

        login.enter_email("notanemail")
        try:
            driver.hide_keyboard()
        except Exception:
            pass

        login.tap_send_otp()

        error = login.get_error_message(timeout=8)

        assert error is not None, (
            "[TC-NEG-01] ❌ No error shown for invalid email"
        )
        assert "invalid" in error or "valid email" in error, (
            f"[TC-NEG-01] ❌ Unexpected error: '{error}'"
        )
        print(f"[TC-NEG-01] ✅ PASSED — error: '{error}'")

        # ── Reset field before next test ──────────────────────────────
        login.clear_email_field()

    # ─────────────────────────────────────────────────────────────────
    # TC-NEG-02 │ Empty email field
    # ─────────────────────────────────────────────────────────────────
    def test_empty_email_shows_error(self, driver):
        """
        GIVEN user is on login screen
        WHEN  they leave email empty and tap Login
        THEN  error 'please enter your email or phone number' appears
        """
        login = LoginPage(driver)
        print("\n[TC-NEG-02] Empty email field test")

        login.wait_for_login_screen()

        # Ensure field is truly empty
        login.clear_email_field()

        try:
            driver.hide_keyboard()
        except Exception:
            pass

        login.tap_send_otp()

        error = login.get_error_message(timeout=8)

        assert error is not None, (
            "[TC-NEG-02] ❌ No error shown for empty email"
        )
        assert "please enter" in error or "enter your email" in error, (
            f"[TC-NEG-02] ❌ Unexpected error: '{error}'"
        )
        print(f"[TC-NEG-02] ✅ PASSED — error: '{error}'")

        # ── Reset field before full login ─────────────────────────────
        login.clear_email_field()

    # ─────────────────────────────────────────────────────────────────
    # TC-POS-01 │ Full login flow (OTP + PIN + power screen)
    # Runs LAST — leaves app on power screen
    # ─────────────────────────────────────────────────────────────────
    def test_full_login_flow(self, driver):

        driver.terminate_app(APP_PACKAGE)
        driver.activate_app(APP_PACKAGE)

        login = LoginPage(driver)
        print("\n[TC-POS-01] Full login flow test")

        login.wait_for_login_screen()

        login.enter_email(TEST_EMAIL)

        try:
            driver.hide_keyboard()
        except Exception:
            pass

        login.tap_send_otp()

        login.wait_for_otp_screen()

        input("🔐 Enter OTP manually then press ENTER...")

        login.tap_verify()

        time.sleep(4)

        if login.wait_for_pin_screen(timeout=20):
            login.handle_pin_if_present(pin=TEST_PIN)

        login.wait_for_power_screen()

        print("[TC-POS-01] ✅ LOGIN FLOW SUCCESS")