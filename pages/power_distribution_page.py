import time
import re
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class PowerDistributionPage:

    # ---------------- LOCATORS ----------------

    POWER_TITLE = (AppiumBy.ACCESSIBILITY_ID, "Power")
    DISTRIBUTION_TITLE = (AppiumBy.ACCESSIBILITY_ID, "Distribution")

    BATTERY_PERCENT = (AppiumBy.XPATH, "//*[contains(@content-desc,'%')]")

    POWER_VALUES = (AppiumBy.XPATH, "//*[contains(@content-desc,'kW')]")

    # FIXED: based on XML (Producing / Consuming / Importing)
    SYSTEM_STATE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc,'Producing') or "
        "contains(@content-desc,'Consuming') or "
        "contains(@content-desc,'Importing')]"
    )

    EXPORT_LABEL = (AppiumBy.ACCESSIBILITY_ID, "This Month's Export")
    IMPORT_LABEL = (AppiumBy.ACCESSIBILITY_ID, "This Month's Import")

    EXPORT_VALUE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc,\"This Month's Export\")]/following::*[1]"
    )

    IMPORT_VALUE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc,\"This Month's Import\")]/following::*[1]"
    )

    SYSTEM_STATUS = (AppiumBy.ACCESSIBILITY_ID, "System Status")

    SWITCH_ICON = (AppiumBy.XPATH, "(//android.widget.ImageView[@clickable='true'])[1]")

    # ---------------- INIT ----------------

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 35)
        print("[PowerDistribution] INIT")

    # ---------------- SCREEN ----------------

    def is_screen_loaded(self):
        try:
            return (
                len(self.driver.find_elements(*self.POWER_TITLE)) > 0 or
                len(self.driver.find_elements(*self.DISTRIBUTION_TITLE)) > 0
            )
        except:
            return False

    def wait_for_screen(self, timeout=40):
        print("[PowerDistribution] Waiting for screen...")

        start = time.time()
        while time.time() - start < timeout:
            if self.is_screen_loaded():
                print("[PowerDistribution] Screen loaded")
                time.sleep(2)
                return True
            time.sleep(2)

        raise TimeoutException("Power Distribution screen did not load")

    # ---------------- POWER ----------------

    def get_all_power_values(self):
        els = self.driver.find_elements(*self.POWER_VALUES)
        values = [e.get_attribute("content-desc") for e in els]
        print("[Power]", values)
        return values

    def validate_power_format(self, v):
        return bool(re.match(r"\d+(\.\d+)?\s*kW", v))

    # ---------------- STATE ----------------

    def get_time_state(self):
        try:
            el = self.driver.find_element(*self.SYSTEM_STATE)
            value = el.get_attribute("content-desc")
            print("[State]", value)
            return value
        except:
            return None

    # ---------------- BATTERY ----------------

    def get_battery_percentage(self):
        try:
            el = self.driver.find_element(*self.BATTERY_PERCENT)
            val = el.get_attribute("content-desc")
            match = re.search(r"\d+%", val or "")
            return match.group() if match else None
        except:
            return None

  

  

    # ---------------- EXPORT / IMPORT ----------------

    def is_export_visible(self):
        return len(self.driver.find_elements(*self.EXPORT_LABEL)) > 0

    def is_import_visible(self):
        return len(self.driver.find_elements(*self.IMPORT_LABEL)) > 0

    def get_export_import_values(self):
        try:
            export = self.driver.find_element(*self.EXPORT_VALUE).get_attribute("content-desc")
            imp = self.driver.find_element(*self.IMPORT_VALUE).get_attribute("content-desc")
            return export, imp
        except:
            return None, None

    # ---------------- SYSTEM ----------------

    def is_system_status_visible(self):
        return len(self.driver.find_elements(*self.SYSTEM_STATUS)) > 0

    # ---------------- ACTION ----------------

    def tap_switch_system(self):
        print("[Action] Tap switch system")

        el = self.wait.until(EC.element_to_be_clickable(self.SWITCH_ICON))
        el.click()
        time.sleep(2)

        self.driver.press_keycode(4)
        time.sleep(2)