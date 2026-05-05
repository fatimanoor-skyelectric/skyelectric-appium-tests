import pytest
import time
from pages.solar_production_page import SolarProductionPage
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="class")
def solar_page(driver):
    """Navigate to Solar Production tab and return the page object."""
    page = SolarProductionPage(driver)
    page.tap_solar_nav()
    return page


@pytest.mark.usefixtures("driver")
class TestSolarProductionPage:

    # ── 1. Page Load ──────────────────────────────────────────────────────────

    def test_page_loads_successfully(self, solar_page):
        """Solar Production title must be visible on screen load."""
        assert solar_page.is_page_loaded(), \
            "Solar Production screen did not load — title not found."

    # ── 2. Default Tab Selection ──────────────────────────────────────────────

    def test_today_tab_is_selected_by_default(self, solar_page):
        """'Today' tab should be the active tab on page open."""
        selected = solar_page.get_selected_tab()
        assert selected == "Today", \
            f"Expected 'Today' tab to be selected, but got '{selected}'."

    # ── 3. Period Tab Navigation ──────────────────────────────────────────────

    def test_tap_this_month_tab(self, solar_page):
        solar_page.tap_this_month_tab()
        assert solar_page.get_selected_tab() == "This Month"

    def test_tap_this_year_tab(self, solar_page):
        solar_page.tap_this_year_tab()
        assert solar_page.get_selected_tab() == "This Year"

    def test_tap_filter_tab(self, solar_page):
        solar_page.tap_filter_tab()
        assert solar_page.get_selected_tab() == "Filter"

    def test_return_to_today_tab(self, solar_page):
        solar_page.tap_today_tab()
        assert solar_page.get_selected_tab() == "Today"

    # ── 4. Production Summary Cards ───────────────────────────────────────────

    def test_today_production_card_is_visible(self, solar_page):
        assert solar_page.is_today_production_card_visible(), \
            "Today's Production card label is not visible."

    def test_yesterday_production_card_is_visible(self, solar_page):
        assert solar_page.is_yesterday_production_card_visible(), \
            "Yesterday's Production card label is not visible."

    def test_today_production_value_is_numeric(self, solar_page):
        value = solar_page.get_today_production_value()
        try:
            assert float(value) >= 0, \
                f"Today's production value is negative: {value}"
        except ValueError:
            pytest.fail(f"Today's production value is not numeric: '{value}'")

    def test_yesterday_production_value_is_numeric(self, solar_page):
        value = solar_page.get_yesterday_production_value()
        try:
            assert float(value) >= 0, \
                f"Yesterday's production value is negative: {value}"
        except ValueError:
            pytest.fail(f"Yesterday's production value is not numeric: '{value}'")

    # ── 5. Production Graph ───────────────────────────────────────────────────

    def test_production_graph_label_is_visible(self, solar_page):
        assert solar_page.is_production_graph_visible(), \
            "'Production Graphs' label not found on screen."

    def test_y_axis_has_all_labels(self, solar_page):
        labels = solar_page.get_visible_y_axis_labels()
        expected = ["0 kW", "1 kW", "2 kW", "3 kW", "4 kW", "5 kW", "6 kW", "7 kW"]
        missing = [lbl for lbl in expected if lbl not in labels]
        assert not missing, f"Missing Y-axis labels: {missing}"

    def test_x_axis_has_all_labels(self, solar_page):
        labels = solar_page.get_visible_x_axis_labels()
        expected = ["04", "06", "08", "10", "12", "14", "16", "18", "20"]
        missing = [h for h in expected if h not in labels]
        assert not missing, f"Missing X-axis labels: {missing}"

    # ── 6. Legend Toggles ─────────────────────────────────────────────────────

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

    # ── 7. Bottom Navigation ──────────────────────────────────────────────────

    def test_solar_tab_is_active_in_bottom_nav(self, solar_page):
        assert solar_page.is_solar_tab_selected_in_bottom_nav(), \
            "Solar tab is not marked as selected in the bottom navigation bar."

    def test_navigate_home_and_back_to_solar(self, solar_page):
        solar_page.tap_home_nav()
        WebDriverWait(solar_page.driver, 2).until(
        lambda d: True
    )
        solar_page.tap_solar_nav()
        assert solar_page.is_page_loaded(), \
            "Could not return to Solar Production screen via bottom nav."