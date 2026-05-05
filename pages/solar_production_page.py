from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SolarProductionPage:
    DEFAULT_WAIT = 10

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_WAIT)

    # ─────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────

    def _find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def _click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _is_visible(self, locator) -> bool:
        try:
            return self.driver.find_element(*locator).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    # ─────────────────────────────────────────────────────────────
    # Scroll FIX (UNCHANGED)
    # ─────────────────────────────────────────────────────────────

    def scroll_to_toggles(self):
        for _ in range(3):
            try:
                switches = self.driver.find_elements(
                    AppiumBy.CLASS_NAME,
                    "android.widget.Switch"
                )
                if switches:
                    return
            except Exception:
                pass

            self.driver.swipe(500, 1600, 500, 800, 800)

    # ─────────────────────────────────────────────────────────────
    # Page Header
    # ─────────────────────────────────────────────────────────────

    TITLE = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Solar")'
    )

    def is_page_loaded(self) -> bool:
        return self._is_visible(self.TITLE)

    # ─────────────────────────────────────────────────────────────
    # Tabs
    # ─────────────────────────────────────────────────────────────

    TAB_TODAY = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Today")'
    )

    TAB_THIS_MONTH = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Month")'
    )

    TAB_THIS_YEAR = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Year")'
    )

    TAB_FILTER = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Filter")'
    )

    def tap_today_tab(self):
        self._click(self.TAB_TODAY)

    def tap_this_month_tab(self):
        self._click(self.TAB_THIS_MONTH)

    def tap_this_year_tab(self):
        self._click(self.TAB_THIS_YEAR)

    def tap_filter_tab(self):
        self._click(self.TAB_FILTER)

    # ─────────────────────────────────────────────────────────────
    # Selected Tab
    # ─────────────────────────────────────────────────────────────

    def get_selected_tab(self) -> str:
        tabs = {
            "Today": self.TAB_TODAY,
            "This Month": self.TAB_THIS_MONTH,
            "This Year": self.TAB_THIS_YEAR,
            "Filter": self.TAB_FILTER,
        }

        for name, locator in tabs.items():
            try:
                el = self.driver.find_element(*locator)
                if el.get_attribute("selected") == "true":
                    return name
            except NoSuchElementException:
                continue

        return "Unknown"

    # ─────────────────────────────────────────────────────────────
    # Production Cards
    # ─────────────────────────────────────────────────────────────

    TODAY_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Today’s Production")'
    )

    YESTERDAY_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Yesterday’s Production")'
    )

    def is_today_production_card_visible(self) -> bool:
        return self._is_visible(self.TODAY_LABEL)

    def is_yesterday_production_card_visible(self) -> bool:
        return self._is_visible(self.YESTERDAY_LABEL)

    # ─────────────────────────────────────────────────────────────
    # Production Values
    # ─────────────────────────────────────────────────────────────

    def get_today_production_value(self) -> str:
        try:
            return self.driver.find_element(
                AppiumBy.XPATH,
                "//*[contains(@content-desc,\"Today’s Production\")]/following::*[1]"
            ).get_attribute("content-desc")
        except Exception:
            return "0"

    def get_yesterday_production_value(self) -> str:
        try:
            return self.driver.find_element(
                AppiumBy.XPATH,
                "//*[contains(@content-desc,\"Yesterday’s Production\")]/following::*[1]"
            ).get_attribute("content-desc")
        except Exception:
            return "0"

    # ─────────────────────────────────────────────────────────────
    # Graph Section
    # ─────────────────────────────────────────────────────────────

    GRAPH_LABEL = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Production Graphs")'
    )

    def is_production_graph_visible(self) -> bool:
        return self._is_visible(self.GRAPH_LABEL)

    def get_visible_y_axis_labels(self):
        labels = []
        expected = [f"{i} kW" for i in range(0, 12)]  # 0 → 11 kW

        for text in expected:
            try:
                el = self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().description("{text}")'
                )
                if el.is_displayed():
                    labels.append(text)
            except NoSuchElementException:
                pass

        return labels

    def get_visible_x_axis_labels(self):
        labels = []
        expected = ["04","06","08","10","12","14","16","18","20"]

        for text in expected:
            try:
                el = self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().description("{text}")'
                )
                if el.is_displayed():
                    labels.append(text)
            except NoSuchElementException:
                pass

        return labels

    # ─────────────────────────────────────────────────────────────
    # Bottom Navigation (FIXED ONLY PART)
    # ─────────────────────────────────────────────────────────────

    HOME_NAV = (AppiumBy.ACCESSIBILITY_ID, "Tab 1 of 5")
    SOLAR_NAV = (AppiumBy.ACCESSIBILITY_ID, "Tab 2 of 5")
    GRID_NAV = (AppiumBy.ACCESSIBILITY_ID, "Tab 3 of 5")
    BATTERY_NAV=(AppiumBy.ACCESSIBILITY_ID, "Tab 4 of 5")
    MORE_NAV = (AppiumBy.ACCESSIBILITY_ID, "Tab 5 of 5")

    def tap_home_nav(self):
        self._click(self.HOME_NAV)

    def tap_solar_nav(self):
        self._click(self.SOLAR_NAV)

    def is_solar_tab_selected_in_bottom_nav(self) -> bool:
        try:
            el = self.driver.find_element(*self.SOLAR_NAV)
            return el.get_attribute("selected") == "true"
        except NoSuchElementException:
            return False