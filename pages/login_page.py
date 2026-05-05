import time
import subprocess
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ADB = '/home/fatima/android-sdk/platform-tools/adb'


def take_screenshot(name):
    path = f'/tmp/{name}.png'
    with open(path, 'wb') as f:
        subprocess.run([ADB, 'exec-out', 'screencap', '-p'], stdout=f)


class LoginPage:

    LOGIN_EMAIL = (AppiumBy.CLASS_NAME, "android.widget.EditText")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Login")
    VERIFY_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Verify")

# ── Locators ──────────────────────────────────────────────
    ERROR_TEXT_CLASS = (AppiumBy.CLASS_NAME, "android.widget.TextView")


    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 25)
        print("[INIT] LoginPage initialized")

    # ---------------- LOGIN SCREEN ----------------

    def wait_for_login_screen(self):
        print("[wait_for_login_screen] START")
        self.wait.until(EC.presence_of_element_located(self.LOGIN_BUTTON))
        print("[wait_for_login_screen] DONE")

    def enter_email(self, email):
        field = self.wait.until(EC.element_to_be_clickable(self.LOGIN_EMAIL))
        field.click()
        time.sleep(1)

        try:
            field.clear()
        except Exception:
            pass

        try:
            field.send_keys(email)
        except Exception:
            field.click()
            time.sleep(1)
            field.send_keys(email)

    def tap_send_otp(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.LOGIN_BUTTON)
        )
        btn.click()

    # ---------------- OTP SCREEN ----------------

    def wait_for_otp_screen(self, timeout=60):
        print("[wait_for_otp_screen] START")

        end = time.time() + timeout
        while time.time() < end:
            otp_fields = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
            verify_btn = self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "Verify")

            if otp_fields and verify_btn:
                print("[wait_for_otp_screen] FOUND")
                return True

            time.sleep(1)

        raise AssertionError("OTP screen not found")

    def tap_verify(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.VERIFY_BUTTON)
        )
        btn.click()




#  ----------------------------------------------------------


    def wait_for_pin_screen(self, timeout=30):
        print("[wait_for_pin_screen] START")

        end = time.time() + timeout

        while time.time() < end:
            page = self.driver.page_source.lower()

            if "lockpassword" in page or "authentication required" in page:
                print("[wait_for_pin_screen] FOUND")
                return True

            time.sleep(1)

        print("[wait_for_pin_screen] NOT FOUND")
        return False
    # ---------------- PIN / SECURITY LOCK ----------------

    def handle_pin_if_present(self, pin="1111"):
        print("[handle_pin_if_present] CHECK")

        page = self.driver.page_source.lower()

        if "lockpassword" in page or "authentication required" in page:
            print("[handle_pin_if_present] PIN screen detected")

            try:
                # 1. Locate element (NO clickable wait)
                pin_field = self.driver.find_element(
                    AppiumBy.ID,
                    "com.android.systemui:id/lockPassword"
                )

                # 2. Force focus
                pin_field.click()
                time.sleep(1)

                # 3. Send PIN directly
                pin_field.send_keys(pin)

                print("[handle_pin_if_present] PIN entered")

                # 4. Press ENTER (important for system UI)
                self.driver.press_keycode(66)

                time.sleep(3)

            except Exception as e:
                print("[PIN ERROR]", e)

        else:
            print("[handle_pin_if_present] No PIN screen")

    # ✅ REQUIRED FIX (for conftest.py compatibility)
    def bypass_security_lock(self, pin="1111"):
        """
        Wrapper used by conftest.py
        """
        print("[bypass_security_lock] START")
        self.handle_pin_if_present(pin)
        print("[bypass_security_lock] DONE")

    # ---------------- POWER SCREEN ----------------

    def is_power_screen(self):
        page = self.driver.page_source.lower()
        return "power" in page and "distribution" in page

    def wait_for_power_screen(self, timeout=60):
        print("[wait_for_power_screen] START")

        end = time.time() + timeout
        while time.time() < end:
            if self.is_power_screen():
                print("[wait_for_power_screen] FOUND")
                return True
            time.sleep(2)

        raise AssertionError("Power screen not loaded")

    # ---------------- FULL OTP LOGIN ----------------

    def login_with_otp(self, email, otp_fetcher_func):
        print("[login_with_otp] START")

        self.wait_for_login_screen()
        self.enter_email(email)
        self.tap_send_otp()
        request_time = time.time()
        self.wait_for_otp_screen()

        # otp = otp_fetcher_func()
        otp = otp_fetcher_func(since_timestamp=request_time)
        print("[OTP]", otp)

        input("🔐 Enter OTP manually then press ENTER...")

        self.tap_verify()
        print("[login_with_otp] OTP submitted, waiting for next screen...")

        time.sleep(5)   # allow transition

        pin_found = self.wait_for_pin_screen(timeout=20)

        if pin_found:
            self.handle_pin_if_present(pin="1111")
        else:
            print("[WARN] PIN screen did not appear")

        self.wait_for_power_screen()

        print("[login_with_otp] DONE")



        

    # ---------------- MAIN ENTRY POINT ----------------

    def handle_app_start(self, email, otp_fetcher_func, pin="1111"):
        print("[handle_app_start] START")

        time.sleep(5)
        page = self.driver.page_source.lower()

        # CASE 1: PIN SCREEN FIRST
        if "lockpassword" in page or "authentication required" in page:
            self.handle_pin_if_present(pin)
            self.wait_for_power_screen()
            return

        # CASE 2: LOGIN SCREEN
        if self.driver.find_elements(*self.LOGIN_BUTTON):
            print("[handle_app_start] LOGIN FLOW")
            self.login_with_otp(email, otp_fetcher_func)
            return

        # CASE 3: ALREADY LOGGED IN
        print("[handle_app_start] Already inside app")
        self.handle_pin_if_present(pin)
        self.wait_for_power_screen()

        print("[handle_app_start] DONE")



        # ── Helpers ───────────────────────────────────────────────

    def clear_email_field(self):
        field = self.wait.until(EC.element_to_be_clickable(self.LOGIN_EMAIL))
        field.click()
        try:
            field.clear()
        except Exception:
            pass

        try:
            self.driver.press_keycode(123)  # move cursor to end
            text = field.text or ""
            for _ in range(len(text)):
                self.driver.press_keycode(67)  # backspace/delete
        except Exception:
            pass

    def get_error_message(self, timeout=8):
        """
        Poll page_source for known error strings.
        Flutter renders errors as plain View text — not always a TextView node.
        """
        known_errors = [
            "invalid email",
            "please enter your email or phone number",
            "enter a valid email",
            "email is not valid",
        ]
        end = time.time() + timeout
        while time.time() < end:
            page = self.driver.page_source.lower()
            for err in known_errors:
                if err in page:
                    print(f"[get_error_message] Found: '{err}'")
                    return err
            time.sleep(0.5)
        return None

    def tap_login_without_otp(self):
        """Just tap Login — used for negative tests, no OTP flow."""
        btn = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
        btn.click()