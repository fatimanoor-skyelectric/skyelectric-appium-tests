"""
Page Object Model for Grid Interaction Screen
App: SkyElectric Smart App (Flutter)
Automation: Appium + ADB
"""

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)


class GridInteractionPage:
    """
    Page Object Model for the Grid Interaction screen.
    Uses content-desc locators extracted from the UI hierarchy XML dump.
    Flutter renders views without resource-ids, so content-desc is the
    primary locator strategy.
    """

    # ──────────────────────────────────────────────
    # Locator Constants
    # ──────────────────────────────────────────────

    # ── Bottom Navigation Tabs ──
    TAB_HOME  = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Tab 1 of 5"]')
    TAB_SOLAR = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Tab 2 of 5"]')
    TAB_GRID  = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Tab 3 of 5"]')
    TAB_BATTERY=(AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Tab 4 of 5"]')
    TAB_MORE  = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Tab 5 of 5"]')
   
   
    # ── Period Toggle Tabs ──
    TAB_TODAY      = (AppiumBy.XPATH, '//android.view.View[@content-desc="Today\nTab 1 of 2"]')
    TAB_THIS_MONTH = (AppiumBy.XPATH, '//android.view.View[@content-desc="This Month\nTab 2 of 2"]')

    # ── Summary Cards (horizontally scrollable) ──
    LABEL_TODAY_IMPORT  = (AppiumBy.XPATH, '//android.view.View[@content-desc="Today\'s Import"]')
    LABEL_TODAY_EXPORT  = (AppiumBy.XPATH, '//android.view.View[@content-desc="Today\'s Export"]')

    VALUE_IMPORT  = (AppiumBy.XPATH, '//android.view.View[@content-desc="9.11"]')   # dynamic – see get_import_value()
    VALUE_EXPORT  = (AppiumBy.XPATH, '//android.view.View[@content-desc="0.18"]')   # dynamic – see get_export_value()

    # Units labels sit next to the values
    # Both share content-desc="Units" – use index to differentiate
    UNITS_IMPORT  = (AppiumBy.XPATH,
        '(//android.view.View[@content-desc="Units"])[1]')
    UNITS_EXPORT  = (AppiumBy.XPATH,
        '(//android.view.View[@content-desc="Units"])[2]')

    # ── Chart Section ──
    GRID_POWER_GRAPH_TITLE = (AppiumBy.XPATH,
        '//android.view.View[@content-desc="Grid Power Graphs"]')

    # Y-axis labels
    Y_LABEL_6KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="6 kW"]')
    Y_LABEL_5KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="5 kW"]')
    Y_LABEL_4KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="4 kW"]')
    Y_LABEL_3KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="3 kW"]')
    Y_LABEL_2KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="2 kW"]')
    Y_LABEL_1KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="1 kW"]')
    Y_LABEL_0KW   = (AppiumBy.XPATH, '//android.view.View[@content-desc="0 kW"]')
    Y_LABEL_NEG1KW= (AppiumBy.XPATH, '//android.view.View[@content-desc="-1 kW"]')

    # X-axis labels (hour markers)
    X_LABEL_00    = (AppiumBy.XPATH, '//android.view.View[@content-desc="00"]')
    X_LABEL_03    = (AppiumBy.XPATH, '//android.view.View[@content-desc="03"]')
    X_LABEL_06    = (AppiumBy.XPATH, '//android.view.View[@content-desc="06"]')
    X_LABEL_09    = (AppiumBy.XPATH, '//android.view.View[@content-desc="09"]')
    X_LABEL_12    = (AppiumBy.XPATH, '//android.view.View[@content-desc="12"]')
    X_LABEL_15    = (AppiumBy.XPATH, '//android.view.View[@content-desc="15"]')
    X_LABEL_18    = (AppiumBy.XPATH, '//android.view.View[@content-desc="18"]')
    X_LABEL_21    = (AppiumBy.XPATH, '//android.view.View[@content-desc="21"]')
    X_LABEL_24    = (AppiumBy.XPATH, '//android.view.View[@content-desc="24"]')

    # ── Yesterday's Data Toggle ──
    YESTERDAY_TOGGLE = (AppiumBy.XPATH, '//android.widget.Switch')
    YESTERDAY_LABEL = (AppiumBy.XPATH,
    '//*[contains(@content-desc,"Yesterday")]')

    # ── Grid section header (semantic landmark) ──
    GRID_SECTION    = (AppiumBy.XPATH, '//android.view.View[@content-desc="Grid"]')
    INTERACTION_SECTION = (AppiumBy.XPATH, '//android.view.View[@content-desc="Interaction"]')

    # ── Phase indicators ──
    PHASE_P1 = (AppiumBy.XPATH, '//android.view.View[@content-desc="P1"]')
    PHASE_P2 = (AppiumBy.XPATH, '//android.view.View[@content-desc="P2"]')
    PHASE_P3 = (AppiumBy.XPATH, '//android.view.View[@content-desc="P3"]')

    # ── Scrollable containers ──
    MAIN_SCROLL_VIEW   = (AppiumBy.CLASS_NAME, 'android.widget.ScrollView')
    SUMMARY_SCROLL_VIEW = (AppiumBy.CLASS_NAME, 'android.widget.HorizontalScrollView')

    # ──────────────────────────────────────────────
    # Constructor
    # ──────────────────────────────────────────────

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ──────────────────────────────────────────────
    # Private Helpers
    # ──────────────────────────────────────────────

    def _find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def _find_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def _is_present(self, locator) -> bool:
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def _get_content_desc(self, locator) -> str:
        return self._find(locator).get_attribute("content-desc")

    def scroll_to_bottom(self):
        try:
            scroll = self.driver.find_element(
                AppiumBy.CLASS_NAME,
                "android.widget.ScrollView"
            )

            self.driver.execute_script("mobile: scrollGesture", {
                "elementId": scroll.id,
                "direction": "down",
                "percent": 1.0
            })

        except Exception:
            size = self.driver.get_window_size()
            self.driver.swipe(
                size['width']//2, int(size['height']*0.8),
                size['width']//2, int(size['height']*0.2),
                800
            )

        return self

    def _scroll_horizontal_right(self):
        element = self._find(self.SUMMARY_SCROLL_VIEW)
        self.driver.swipe(
            start_x=int(element.size['width'] * 0.8),
            start_y=element.location['y'] + element.size['height'] // 2,
            end_x=int(element.size['width'] * 0.2),
            end_y=element.location['y'] + element.size['height'] // 2,
            duration=600
        )

    # ──────────────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────────────

    def navigate_to_grid_tab(self):
        """Tap the Grid (Tab 3 of 5) bottom navigation icon."""
        logger.info("Navigating to Grid Interaction tab")
        self._find_clickable(self.TAB_GRID).click()
        return self

    def navigate_to_home_tab(self):
        self._find_clickable(self.TAB_HOME).click()
        return self

    def navigate_to_solar_tab(self):
        self._find_clickable(self.TAB_SOLAR).click()
        return self

    def navigate_to_more_tab(self):
        self._find_clickable(self.TAB_MORE).click()
        return self

    # ──────────────────────────────────────────────
    # Period Toggle
    # ──────────────────────────────────────────────

    def tap_today_tab(self):
        """Select the 'Today' period tab."""
        logger.info("Tapping Today tab")
        self._find_clickable(self.TAB_TODAY).click()
        return self

    def tap_this_month_tab(self):
        """Select the 'This Month' period tab."""
        logger.info("Tapping This Month tab")
        self._find_clickable(self.TAB_THIS_MONTH).click()
        return self

    def is_today_tab_selected(self) -> bool:
        el = self._find(self.TAB_TODAY)
        return el.get_attribute("selected") == "true"

    def is_this_month_tab_selected(self) -> bool:
        el = self._find(self.TAB_THIS_MONTH)
        return el.get_attribute("selected") == "true"

    # ──────────────────────────────────────────────
    # Summary Card Values
    # ──────────────────────────────────────────────

    def get_import_value(self) -> str:
        """
        Return the numeric import value string shown on the card.
        Uses a dynamic XPath – the content-desc IS the numeric value.
        Fetches the sibling view next to 'Today's Import' label.
        """
        # Locate by position: first numeric view after the import label
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//android.view.View[contains(@content-desc, ".")]'
        )
        if elements:
            return elements[0].get_attribute("content-desc")
        raise NoSuchElementException("Import value element not found")

    def get_export_value(self) -> str:
        """Return the numeric export value string shown on the card."""
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//android.view.View[contains(@content-desc, ".")]'
        )
        if len(elements) >= 2:
            return elements[1].get_attribute("content-desc")
        raise NoSuchElementException("Export value element not found")

    def is_today_import_label_visible(self) -> bool:
        return self._is_present(self.LABEL_TODAY_IMPORT)

    def is_today_export_label_visible(self) -> bool:
        return self._is_present(self.LABEL_TODAY_EXPORT)

    def scroll_summary_cards_right(self):
        """Horizontally scroll the summary card strip to reveal more cards."""
        self._scroll_horizontal_right()
        return self

    # ──────────────────────────────────────────────
    # Chart Verification
    # ──────────────────────────────────────────────

    def is_grid_power_graph_visible(self) -> bool:
        return self._is_present(self.GRID_POWER_GRAPH_TITLE)

    def get_y_axis_labels(self) -> list:
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//android.view.View[contains(@content-desc,"kW")]'
        )

        labels = []
        for el in elements:
            text = el.get_attribute("content-desc")

            # match pattern like: 4 kW, -2 kW
            if text and text.replace(" kW", "").replace("-", "").isdigit():
                labels.append(text)

        return labels

    def get_x_axis_labels(self) -> list:
        """Return all visible X-axis hour labels as a list of strings."""
        labels_locators = [
            self.X_LABEL_00, self.X_LABEL_03, self.X_LABEL_06,
            self.X_LABEL_09, self.X_LABEL_12, self.X_LABEL_15,
            self.X_LABEL_18, self.X_LABEL_21, self.X_LABEL_24
        ]
        result = []
        for loc in labels_locators:
            try:
                el = self.driver.find_element(*loc)
                result.append(el.get_attribute("content-desc"))
            except NoSuchElementException:
                pass
        return result

    # ──────────────────────────────────────────────
    # Yesterday Toggle
    # ──────────────────────────────────────────────

    def is_yesterday_toggle_on(self) -> bool:
        el = self._find(self.YESTERDAY_TOGGLE)
        return el.get_attribute("checked") == "true"

    def toggle_yesterday_data(self):
        """Toggle the Yesterday's Data switch."""
        logger.info("Toggling Yesterday's Data switch")
        self._find_clickable(self.YESTERDAY_TOGGLE).click()
        return self

    def enable_yesterday_data(self):
        if not self.is_yesterday_toggle_on():
            self.toggle_yesterday_data()
        return self

    def disable_yesterday_data(self):
        if self.is_yesterday_toggle_on():
            self.toggle_yesterday_data()
        return self

    def is_yesterday_label_visible(self) -> bool:
        return self._is_present(self.YESTERDAY_LABEL)

    # ──────────────────────────────────────────────
    # Phase Indicators
    # ──────────────────────────────────────────────

    def are_phase_indicators_visible(self) -> bool:
        return (
            self._is_present(self.PHASE_P1) and
            self._is_present(self.PHASE_P2) and
            self._is_present(self.PHASE_P3)
        )

    # ──────────────────────────────────────────────
    # Screen State
    # ──────────────────────────────────────────────

    def is_screen_loaded(self) -> bool:
        """Verify the Grid Interaction screen is fully loaded."""
        try:
            self._find(self.TAB_TODAY)
            self._find(self.LABEL_TODAY_IMPORT)
            self._find(self.LABEL_TODAY_EXPORT)
            return True
        except TimeoutException:
            return False

    def scroll_to_bottom(self):
        """Scroll main view to reveal Grid Voltages and other below-fold content."""
        self._scroll_down()
        return self

    def wait_for_screen(self):
        """Block until the Grid Interaction screen is fully loaded."""
        self.wait.until(
            lambda d: self.is_screen_loaded(),
            message="Grid Interaction screen did not load in time"
        )
        return self