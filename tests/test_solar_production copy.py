from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SolarProductionPage:
    """
    Page Object Model for the Solar Production screen.
    App: com.skyelectric.smartapp (Flutter)
    Automation: Appium + UIAutomator2
    """

    DEFAULT_WAIT = 10

    # ─── Page Title ───────────────────────────────────────────────────────────
    SOLAR_PRODUCTION_TITLE = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Solar\\nProduction")',
    )

    # ─── Period Tabs ──────────────────────────────────────────────────────────
    TAB_TODAY = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Today\\nTab 1 of 4")',
    )
    TAB_THIS_MONTH = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("This Month\\nTab 2 of 4")',
    )
    TAB_THIS_YEAR = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("This Year\\nTab 3 of 4")',
    )
    TAB_FILTER = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Filter\\nTab 4 of 4")',
    )

    # ─── Production Summary Cards ─────────────────────────────────────────────
    CARD_TODAY_PRODUCTION_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Today\'s Production")',
    )
    CARD_YESTERDAY_PRODUCTION_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Yesterday\'s Production")',
    )

    # ─── Production Graph ─────────────────────────────────────────────────────
    PRODUCTION_GRAPHS_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Production Graphs")',
    )

    Y_AXIS_LABELS = ["0 kW", "1 kW", "2 kW", "3 kW", "4 kW", "5 kW", "6 kW", "7 kW"]
    X_AXIS_LABELS = ["04", "06", "08", "10", "12", "14", "16", "18", "20"]

    # ─── Legend Toggles ───────────────────────────────────────────────────────
    YESTERDAY_DATA_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Yesterday\'s Data")',
    )
    TOMORROW_FORECAST_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Tomorrow\'s Forecast")',
    )
    YESTERDAY_DATA_TOGGLE = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Switch").instance(0)',
    )
    TOMORROW_FORECAST_TOGGLE = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Switch").instance(1)',
    )

    # ─── Bottom Navigation ────────────────────────────────────────────────────
    BOTTOM_NAV_HOME  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Tab 1 of 4").className("android.widget.ImageView")')
    BOTTOM_NAV_SOLAR = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Tab 2 of 4").className("android.widget.ImageView")')
    BOTTOM_NAV_GRID  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Tab 3 of 4").className("android.widget.ImageView")')
    BOTTOM_NAV_MORE  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Tab 4 of 4").className("android.widget.ImageView")')

    # ─────────────────────────────────────────────────────────────────────────

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_WAIT)

    # ─── Private Helpers ──────────────────────────────────────────────────────

    def _find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def _click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _is_displayed(self, locator) -> bool:
        try:
            return self._find(locator).is_displayed()
        except TimeoutException:
            return False

    def _scroll_down(self):
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.7)
        end_y   = int(size["height"] * 0.3)
        self.driver.swipe(start_x, start_y, start_x, end_y, 600)

    # ─── Page Load ────────────────────────────────────────────────────────────

    def is_page_loaded(self) -> bool:
        return self._is_displayed(self.SOLAR_PRODUCTION_TITLE)

    # ─── Period Tabs ──────────────────────────────────────────────────────────

    def tap_today_tab(self):
        self._click(self.TAB_TODAY)

    def tap_this_month_tab(self):
        self._click(self.TAB_THIS_MONTH)

    def tap_this_year_tab(self):
        self._click(self.TAB_THIS_YEAR)

    def tap_filter_tab(self):
        self._click(self.TAB_FILTER)

    def get_selected_tab(self) -> str:
        tabs = {
            "Today":      self.TAB_TODAY,
            "This Month": self.TAB_THIS_MONTH,
            "This Year":  self.TAB_THIS_YEAR,
            "Filter":     self.TAB_FILTER,
        }
        for name, locator in tabs.items():
            try:
                el = self.driver.find_element(*locator)
                if el.get_attribute("selected") == "true":
                    return name
            except NoSuchElementException:
                pass
        return "Unknown"

    # ─── Production Values ────────────────────────────────────────────────────

    def get_today_production_value(self) -> str:
        el = self.wait.until(
            EC.presence_of_element_located((
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("android.view.View")'
                '.descriptionMatches("\\\\d+\\\\.\\\\d+").instance(0)',
            ))
        )
        return el.get_attribute("content-desc")

    def get_yesterday_production_value(self) -> str:
        el = self.wait.until(
            EC.presence_of_element_located((
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("android.view.View")'
                '.descriptionMatches("\\\\d+\\\\.\\\\d+").instance(1)',
            ))
        )
        return el.get_attribute("content-desc")

    def is_today_production_card_visible(self) -> bool:
        return self._is_displayed(self.CARD_TODAY_PRODUCTION_LABEL)

    def is_yesterday_production_card_visible(self) -> bool:
        return self._is_displayed(self.CARD_YESTERDAY_PRODUCTION_LABEL)

    # ─── Graph ────────────────────────────────────────────────────────────────

    def is_production_graph_visible(self) -> bool:
        return self._is_displayed(self.PRODUCTION_GRAPHS_LABEL)

    def get_visible_y_axis_labels(self) -> list:
        labels = []
        for desc in self.Y_AXIS_LABELS:
            try:
                el = self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().description("{desc}")',
                )
                if el.is_displayed():
                    labels.append(desc)
            except NoSuchElementException:
                pass
        return labels

    def get_visible_x_axis_labels(self) -> list:
        labels = []
        for hour in self.X_AXIS_LABELS:
            try:
                el = self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().description("{hour}")',
                )
                if el.is_displayed():
                    labels.append(hour)
            except NoSuchElementException:
                pass
        return labels

    # ─── Toggles ──────────────────────────────────────────────────────────────

    def scroll_to_toggles(self):
        for _ in range(3):
            if self._is_displayed(self.YESTERDAY_DATA_LABEL):
                break
            self._scroll_down()

    def is_yesterday_data_toggle_on(self) -> bool:
        el = self._find(self.YESTERDAY_DATA_TOGGLE)
        return el.get_attribute("checked") == "true"

    def is_tomorrow_forecast_toggle_on(self) -> bool:
        el = self._find(self.TOMORROW_FORECAST_TOGGLE)
        return el.get_attribute("checked") == "true"

    def toggle_yesterday_data(self):
        self._click(self.YESTERDAY_DATA_TOGGLE)

    def toggle_tomorrow_forecast(self):
        self._click(self.TOMORROW_FORECAST_TOGGLE)

    # ─── Bottom Navigation ────────────────────────────────────────────────────

    def tap_home_nav(self):
        self._click(self.BOTTOM_NAV_HOME)

    def tap_solar_nav(self):
        self._click(self.BOTTOM_NAV_SOLAR)

    def tap_grid_nav(self):
        self._click(self.BOTTOM_NAV_GRID)

    def tap_more_nav(self):
        self._click(self.BOTTOM_NAV_MORE)

    def is_solar_tab_selected_in_bottom_nav(self) -> bool:
        el = self._find(self.BOTTOM_NAV_SOLAR)
        return el.get_attribute("selected") == "true"