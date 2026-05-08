from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MenuOptionsPage:
    """
    Page Object for the Menu Options screen.
    The screen lives behind Tab 5 of 5 in the bottom navigation bar.
    All menu items are ImageView nodes with content-desc — no resource-ids.
    Locator strategy: ACCESSIBILITY_ID (maps to content-desc on Android).
    SmartFlow section is intentionally excluded.
    """

    # ── Locators ─────────────────────────────────────────────────────────────

    # Bottom navigation — Tab 5 opens Menu Options
    TAB_MENU_OPTIONS = (AppiumBy.ACCESSIBILITY_ID, "Tab 5 of 5")

    # Header (content-desc has a real newline in the XML: &#10;)
    HEADER = (AppiumBy.ACCESSIBILITY_ID, "Menu\nOptions")

    # Menu items
    SYSTEM_INFORMATION    = (AppiumBy.ACCESSIBILITY_ID, "System Information")
    ENERGY_SAVING_REPORTS = (AppiumBy.ACCESSIBILITY_ID, "Energy Saving Reports")
    REFER_A_FRIEND        = (AppiumBy.ACCESSIBILITY_ID, "Refer a Friend")
    TRACK_ORDER           = (AppiumBy.ACCESSIBILITY_ID, "Track Order")
    POLICIES_AND_FAQS     = (AppiumBy.ACCESSIBILITY_ID, "Policies & FAQs")
    TUTORIALS_AND_UPDATES = (AppiumBy.ACCESSIBILITY_ID, "Tutorials & Updates")
    SETTINGS              = (AppiumBy.ACCESSIBILITY_ID, "Settings")

    # Ordered list of every expected menu label
    ALL_MENU_LABELS = [
        "System Information",
        "Energy Saving Reports",
        "Refer a Friend",
        "Track Order",
        "Policies & FAQs",
        "Tutorials & Updates",
        "Settings",
    ]

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _find(self, locator):
        # Wait until the element is visible on screen
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _find_clickable(self, locator):
        # On Android ImageViews, visibility is usually enough to tap
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _is_displayed(self, locator) -> bool:
        try:
            return self._find(locator).is_displayed()
        except Exception:
            return False

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self):
        """
        Taps Tab 5 in the bottom nav bar to open the Menu Options screen
        and waits until the header is visible.
        Call this at the start of every test (or once in a fixture).
        """
        self._find_clickable(self.TAB_MENU_OPTIONS).click()
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        return self

    # ── Page-level checks ─────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self._is_displayed(self.HEADER)

    # ── Individual item visibility ────────────────────────────────────────────

    def is_system_information_displayed(self) -> bool:
        return self._is_displayed(self.SYSTEM_INFORMATION)

    def is_energy_saving_reports_displayed(self) -> bool:
        return self._is_displayed(self.ENERGY_SAVING_REPORTS)

    def is_refer_a_friend_displayed(self) -> bool:
        return self._is_displayed(self.REFER_A_FRIEND)

    def is_track_order_displayed(self) -> bool:
        return self._is_displayed(self.TRACK_ORDER)

    def is_policies_and_faqs_displayed(self) -> bool:
        return self._is_displayed(self.POLICIES_AND_FAQS)

    def is_tutorials_and_updates_displayed(self) -> bool:
        return self._is_displayed(self.TUTORIALS_AND_UPDATES)

    def is_settings_displayed(self) -> bool:
        return self._is_displayed(self.SETTINGS)

    def all_menu_items_displayed(self) -> dict:
        """Returns {label: bool} for every expected menu item."""
        return {
            label: self._is_displayed((AppiumBy.ACCESSIBILITY_ID, label))
            for label in self.ALL_MENU_LABELS
        }

    # ── Tap actions ───────────────────────────────────────────────────────────

    def tap_system_information(self):
        self._find_clickable(self.SYSTEM_INFORMATION).click()

    def tap_energy_saving_reports(self):
        self._find_clickable(self.ENERGY_SAVING_REPORTS).click()

    def tap_refer_a_friend(self):
        self._find_clickable(self.REFER_A_FRIEND).click()

    def tap_track_order(self):
        self._find_clickable(self.TRACK_ORDER).click()

    def tap_policies_and_faqs(self):
        self._find_clickable(self.POLICIES_AND_FAQS).click()

    def tap_tutorials_and_updates(self):
        self._find_clickable(self.TUTORIALS_AND_UPDATES).click()

    def tap_settings(self):
        self._find_clickable(self.SETTINGS).click()