from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class BatteryManagementPage:
    """
    Page Object Model for the Battery Management screen.

    Layout (top → bottom, scrollable):
    ┌─────────────────────────────────────┐
    │  Battery % indicator  (100 %)       │
    │  At Current Load  |  Stored Power   │
    │  Battery Usage Graph                │
    │    Y-axis: 1 kW / 0 kW / -1 kW     │
    │    X-axis: 00 03 06 … 24            │
    │  Yesterday's Data toggle  [1]       │  ← toggle index 0
    │  Battery SOC Graph                  │
    │    Y-axis: 100% 80% 60% 40% 20% 0% │
    │    X-axis: 00 03 06 … 24            │
    │  Yesterday's Data toggle  [2]       │  ← toggle index 1
    └─────────────────────────────────────┘
    """

    DEFAULT_WAIT = 15

    # ── SOC indicator (top card) ──────────────────────────────────────────────
    SOC_INDICATOR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc,'%')]"
    )

    # ── Battery Usage Graph — Y-axis ─────────────────────────────────────────
    USAGE_Y_1KW    = (AppiumBy.ACCESSIBILITY_ID, "1 kW")
    USAGE_Y_0KW    = (AppiumBy.ACCESSIBILITY_ID, "0 kW")
    USAGE_Y_NEG1KW = (AppiumBy.ACCESSIBILITY_ID, "-1 kW")

    # ── Battery Usage Graph — X-axis ─────────────────────────────────────────
    USAGE_X_00 = (AppiumBy.ACCESSIBILITY_ID, "00")
    USAGE_X_03 = (AppiumBy.ACCESSIBILITY_ID, "03")
    USAGE_X_06 = (AppiumBy.ACCESSIBILITY_ID, "06")
    USAGE_X_09 = (AppiumBy.ACCESSIBILITY_ID, "09")
    USAGE_X_12 = (AppiumBy.ACCESSIBILITY_ID, "12")
    USAGE_X_15 = (AppiumBy.ACCESSIBILITY_ID, "15")
    USAGE_X_18 = (AppiumBy.ACCESSIBILITY_ID, "18")
    USAGE_X_21 = (AppiumBy.ACCESSIBILITY_ID, "21")
    USAGE_X_24 = (AppiumBy.ACCESSIBILITY_ID, "24")

    USAGE_X_ALL = [
        USAGE_X_00, USAGE_X_03, USAGE_X_06, USAGE_X_09, USAGE_X_12,
        USAGE_X_15, USAGE_X_18, USAGE_X_21, USAGE_X_24,
    ]

    # ── Yesterday's Data toggles ──────────────────────────────────────────────
    # The Usage toggle is the 1st Switch in the hierarchy (above SOC Graph).
    # The SOC toggle is the 2nd Switch (below SOC Graph header).
    YESTERDAY_TOGGLE_USAGE = (
        AppiumBy.XPATH,
        "(//android.widget.Switch)[1]"
    )

    YESTERDAY_TOGGLE_SOC = (
        AppiumBy.XPATH,
        "(//android.widget.Switch)[2]"
    )

    # ── Yesterday's Data label ────────────────────────────────────────────────
    YESTERDAY_LABEL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc,'Yesterday')]"
    )

    # ── Battery SOC Graph header ──────────────────────────────────────────────
    SOC_GRAPH_HEADER = (AppiumBy.ACCESSIBILITY_ID, "Battery SOC Graph")

    # ── Battery SOC Graph — Y-axis ────────────────────────────────────────────
    SOC_Y_100 = (AppiumBy.ACCESSIBILITY_ID, "100 %")
    SOC_Y_80  = (AppiumBy.ACCESSIBILITY_ID, "80 %")
    SOC_Y_60  = (AppiumBy.ACCESSIBILITY_ID, "60 %")
    SOC_Y_40  = (AppiumBy.ACCESSIBILITY_ID, "40 %")
    SOC_Y_20  = (AppiumBy.ACCESSIBILITY_ID, "20 %")
    SOC_Y_0   = (AppiumBy.ACCESSIBILITY_ID, "0 %")

    SOC_Y_ALL        = [SOC_Y_100, SOC_Y_80, SOC_Y_60, SOC_Y_40, SOC_Y_20, SOC_Y_0]
    SOC_Y_ALL_LABELS = ["100 %", "80 %", "60 %", "40 %", "20 %", "0 %"]

    # ── Bottom navigation tabs ────────────────────────────────────────────────
    TAB_1 = (AppiumBy.ACCESSIBILITY_ID, "Tab 1 of 5")
    TAB_2 = (AppiumBy.ACCESSIBILITY_ID, "Tab 2 of 5")
    TAB_3 = (AppiumBy.ACCESSIBILITY_ID, "Tab 3 of 5")
    TAB_4 = (AppiumBy.ACCESSIBILITY_ID, "Tab 4 of 5")  # Battery (active)
    TAB_5 = (AppiumBy.ACCESSIBILITY_ID, "Tab 5 of 5")

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_WAIT)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def _find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _is_visible(self, locator) -> bool:
        try:
            return self._find_visible(locator).is_displayed()
        except Exception:
            return False

    def _is_checked(self, el) -> bool:
        for attr in ["checked", "selected", "value"]:
            val = el.get_attribute(attr)
            if val is not None:
                return str(val).lower() in ["true", "1", "selected"]
        return False
    def _tap_element(self, el):
        """Reliably tap any element using its center coordinates."""
        rect = el.rect
        x = rect["x"] + rect["width"] // 2
        y = rect["y"] + rect["height"] // 2
        self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})


    def _scroll_up(self):
        """Swipe downward to reveal content above the fold."""
        size    = self.driver.get_window_size()
        x       = size["width"] // 2
        start_y = int(size["height"] * 0.25)
        end_y   = int(size["height"] * 0.75)
        self.driver.swipe(x, start_y, x, end_y, duration=600)

    def scroll_to_usage_toggle(self):
        """
        Scroll so the first Switch (Usage graph Yesterday toggle) is on-screen.
        Called automatically by get_usage_yesterday_toggle() so taps always land.
        """
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true))'
                '.scrollIntoView(new UiSelector()'
                '.className("android.widget.Switch").instance(0))'
            )
            return
        except Exception:
            pass

        # Fallback — swipe upward until the toggle is visible
        for _ in range(6):
            if self._is_visible(self.YESTERDAY_TOGGLE_USAGE):
                return
            self._scroll_up()
            time.sleep(0.4)

    def _scroll_down(self):
        """
        Perform a single upward swipe to reveal content below the fold.
        Uses W3C Actions so it works on both UiAutomator2 and XCUITest.
        """
        size    = self.driver.get_window_size()
        x       = size["width"] // 2
        start_y = int(size["height"] * 0.75)
        end_y   = int(size["height"] * 0.25)
        self.driver.swipe(x, start_y, x, end_y, duration=600)

    # ── Scroll helpers ────────────────────────────────────────────────────────

    def scroll_to_soc_graph(self):
        """
        Scroll until the 'Battery SOC Graph' header is visible.
        Tries UiScrollable first (fast), falls back to manual swipes.
        """
        # Fast path — UiScrollable
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true))'
                '.scrollIntoView(new UiSelector().descriptionContains("Battery SOC Graph"))'
            )
            return
        except Exception:
            pass

        # Fallback — manual swipes (up to 8 attempts)
        for _ in range(8):
            if self._is_visible(self.SOC_GRAPH_HEADER):
                return
            self._scroll_down()
            time.sleep(0.4)

    def scroll_to_soc_toggle(self):
        """
        Scroll until the second Switch (SOC yesterday toggle) is present in DOM.
        Uses UiScrollable to bring the SOC graph's toggle row into view.
        """
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true))'
                '.scrollIntoView(new UiSelector().className("android.widget.Switch").instance(1))'
            )
            return
        except Exception:
            pass

        # Fallback
        self.scroll_to_soc_graph()
        for _ in range(4):
            try:
                self.driver.find_elements(AppiumBy.XPATH, "//android.widget.Switch")
                if len(self.driver.find_elements(AppiumBy.XPATH, "//android.widget.Switch")) >= 2:
                    return
            except Exception:
                pass
            self._scroll_down()
            time.sleep(0.4)

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_to_tab(self, tab_number: int):
        """Tap a bottom-nav tab (1–5)."""
        tab_map = {
            1: self.TAB_1, 2: self.TAB_2, 3: self.TAB_3,
            4: self.TAB_4, 5: self.TAB_5,
        }
        self._find(tab_map[tab_number]).click()

    def get_active_tab(self):
        """Return the currently selected bottom-nav tab element."""
        for loc in (self.TAB_1, self.TAB_2, self.TAB_3, self.TAB_4, self.TAB_5):
            try:
                el = self._find(loc)
                if el.get_attribute("selected") == "true":
                    return el
            except Exception:
                pass
        return None

    # ── SOC indicator (top card) ──────────────────────────────────────────────

    def get_soc_indicator(self):
        return self._find_visible(self.SOC_INDICATOR)

    def is_battery_full(self) -> bool:
        return self._is_visible(self.SOC_INDICATOR)

    # ── Battery Usage Graph ───────────────────────────────────────────────────

    def get_usage_graph_y_labels(self):
        return self.driver.find_elements(
            AppiumBy.XPATH,
            "//*[contains(@content-desc,'kW')]"
        )

    def get_usage_graph_x_labels(self) -> list:
        labels = []
        for loc in self.USAGE_X_ALL:
            try:
                labels.append(self._find_visible(loc))
            except Exception:
                pass
        return labels

    # ── Yesterday's Data — Usage Graph toggle ────────────────────────────────

    def get_usage_yesterday_toggle(self):
        """Scroll so the Usage toggle is on-screen, then return it."""
        self.scroll_to_usage_toggle()
        return self._find(self.YESTERDAY_TOGGLE_USAGE)

    def is_usage_yesterday_toggle_on(self) -> bool:
        return self._is_checked(self.get_usage_yesterday_toggle())

    def tap_usage_yesterday_toggle(self):
        el     = self.get_usage_yesterday_toggle()
        before = self._is_checked(el)
        self._tap_element(el)
        self.wait.until(
            lambda d: self._is_checked(self.get_usage_yesterday_toggle()) != before
        )

    def set_usage_yesterday_toggle(self, enable: bool):
        """Ensure the Usage toggle is in the desired state."""
        if self.is_usage_yesterday_toggle_on() != enable:
            self.tap_usage_yesterday_toggle()

    # ── Battery SOC Graph ─────────────────────────────────────────────────────

    def is_soc_graph_header_visible(self) -> bool:
        return self._is_visible(self.SOC_GRAPH_HEADER)

    def get_soc_graph_y_labels(self) -> list:
        """Return all visible Y-axis % label elements for the SOC graph."""
        self.scroll_to_soc_graph()
        labels = []
        for loc in self.SOC_Y_ALL:
            try:
                labels.append(self._find_visible(loc))
            except Exception:
                pass
        return labels

    def get_soc_graph_x_labels(self) -> list:
        """Return visible X-axis hour labels under the SOC graph."""
        self.scroll_to_soc_graph()
        labels = []
        for loc in self.USAGE_X_ALL:
            try:
                labels.append(self._find_visible(loc))
            except Exception:
                pass
        return labels

    # ── Yesterday's Data — SOC Graph toggle ──────────────────────────────────

    def get_soc_yesterday_toggle(self):
        """Scroll so the SOC toggle is on-screen, then return it."""
        self.scroll_to_soc_toggle()
        return self._find(self.YESTERDAY_TOGGLE_SOC)

    def is_soc_yesterday_toggle_on(self) -> bool:
        return self._is_checked(self.get_soc_yesterday_toggle())

    def tap_soc_yesterday_toggle(self):
        el     = self.get_soc_yesterday_toggle()
        before = self._is_checked(el)
        self._tap_element(el)
        self.wait.until(
            lambda d: self._is_checked(self.get_soc_yesterday_toggle()) != before
        )

    def set_soc_yesterday_toggle(self, enable: bool):
        """Ensure the SOC toggle is in the desired state."""
        if self.is_soc_yesterday_toggle_on() != enable:
            self.tap_soc_yesterday_toggle()

    # ── Shared label ─────────────────────────────────────────────────────────

    def is_yesterday_label_visible(self) -> bool:
        return self._is_visible(self.YESTERDAY_LABEL)