from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
    SOC_INDICATOR = (AppiumBy.XPATH, "//*[contains(@content-desc,'SOC')]")

    # ── Battery Usage Graph — Y-axis ─────────────────────────────────────────
    USAGE_Y_1KW    = (AppiumBy.ACCESSIBILITY_ID, "1 kW")
    USAGE_Y_0KW    = (AppiumBy.ACCESSIBILITY_ID, "0 kW")
    USAGE_Y_NEG1KW = (AppiumBy.ACCESSIBILITY_ID, "-1 kW")

    # ── Battery Usage Graph — X-axis ─────────────────────────────────────────
    # NOTE: The XML has TWO sets of 00–24 labels (one per graph).
    # ACCESSIBILITY_ID matches the first occurrence which belongs to Usage graph.
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

    # ── Yesterday's Data toggles ─────────────────────────────────────────────
    # Two android.widget.Switch nodes exist — one below each graph.
    # Addressed by UiAutomator2 instance index (0-based).
    YESTERDAY_TOGGLE_USAGE = (
        AppiumBy.XPATH,
        '(//android.widget.Switch)[1]'
    )

    YESTERDAY_TOGGLE_SOC = (
        AppiumBy.XPATH,
        '(//android.widget.Switch)[2]'
    )

    # ── Yesterday's Data label ────────────────────────────────────────────────
    YESTERDAY_LABEL = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textMatches("(?i).*yesterday.*")'
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

    def _scroll_down(self):
        """Swipe up to reveal content below the fold."""
        size = self.driver.get_window_size()
        x        = size["width"] // 2
        start_y  = int(size["height"] * 0.75)
        end_y    = int(size["height"] * 0.25)
        self.driver.swipe(x, start_y, x, end_y, duration=600)

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
            "//*[contains(@text,'kW')]"
        )

    def get_usage_graph_x_labels(self) -> list:
        labels = []
        for loc in self.USAGE_X_ALL:
            try:
                labels.append(self._find_visible(loc))
            except Exception:
                pass
        return labels

    # ── Yesterday's Data — Usage Graph toggle (instance 0) ───────────────────

    def get_usage_yesterday_toggle(self):
        return self._find(self.YESTERDAY_TOGGLE_USAGE)

    def is_soc_yesterday_toggle_on(self) -> bool:
        el = self.get_soc_yesterday_toggle()
        return el.get_attribute("checked") in ["true", True]

    def tap_usage_yesterday_toggle(self):
        self.get_usage_yesterday_toggle().click()
        self.wait.until(lambda d: True)  # small sync buffer

    def is_usage_yesterday_toggle_on(self) -> bool:
        el = self.get_usage_yesterday_toggle()
        return el.get_attribute("checked") in ["true", True]

    # ── Battery SOC Graph ─────────────────────────────────────────────────────

    def scroll_to_soc_graph(self):
        """Scroll down until the SOC Graph header is visible (max 4 swipes)."""
        for _ in range(4):
            if self._is_visible(self.SOC_GRAPH_HEADER):
                return
            self._scroll_down()

    def is_soc_graph_header_visible(self) -> bool:
        return self._is_visible(self.SOC_GRAPH_HEADER)

    def get_soc_graph_y_labels(self) -> list:
        """Return all visible Y-axis % label elements for the SOC graph."""
        labels = []
        for loc in self.SOC_Y_ALL:
            try:
                labels.append(self._find_visible(loc))
            except Exception:
                pass
        return labels

    def get_soc_graph_x_labels(self) -> list:
        """Return visible X-axis hour labels under the SOC graph."""
        labels = []
        for loc in self.USAGE_X_ALL:
            try:
                labels.append(self._find_visible(loc))
            except Exception:
                pass
        return labels

    # ── Yesterday's Data — SOC Graph toggle (instance 1) ─────────────────────

    def get_soc_yesterday_toggle(self):
        return self._find(self.YESTERDAY_TOGGLE_SOC)

    def is_soc_yesterday_toggle_on(self) -> bool:
        return self.get_soc_yesterday_toggle().get_attribute("checked") == "true"

    def tap_soc_yesterday_toggle(self):
        el = self.get_soc_yesterday_toggle()
        el.click()
        self.wait.until(lambda d: el.get_attribute("checked") in ["true", "false"])

    # ── Shared label ─────────────────────────────────────────────────────────

    def is_yesterday_label_visible(self) -> bool:
        return self._is_visible(self.YESTERDAY_LABEL)


