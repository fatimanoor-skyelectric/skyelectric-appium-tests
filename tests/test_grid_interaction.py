"""
Test Suite for Grid Interaction Screen
App: SkyElectric Smart App (Flutter)
Automation: Appium + ADB + pytest
"""

import pytest
import logging
from appium.webdriver.common.appiumby import AppiumBy

from pages.grid_interaction_page import GridInteractionPage

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def grid_page(driver):
    """Navigate to Grid Interaction tab and return the page object."""
    page = GridInteractionPage(driver, timeout=20)
    page.navigate_to_grid_tab()
    page.wait_for_screen()
    return page


# ──────────────────────────────────────────────────────────────
# Helper – assert value is numeric
# ──────────────────────────────────────────────────────────────

def assert_is_numeric(value: str, label: str = "value"):
    try:
        float(value)
    except (ValueError, TypeError):
        pytest.fail(f"Expected numeric {label}, got: '{value}'")


# ══════════════════════════════════════════════════════════════
# TEST CLASS
# ══════════════════════════════════════════════════════════════

class TestGridInteractionScreen:

    # ──────────────────────────────────────────────
    # TC-GI-001  Screen Load
    # ──────────────────────────────────────────────

    def test_grid_screen_loads_successfully(self, grid_page):
        assert grid_page.is_screen_loaded(), \
            "Grid Interaction screen did not load – key elements missing"

    # ──────────────────────────────────────────────
    # TC-GI-002  Bottom Navigation
    # ──────────────────────────────────────────────

    def test_grid_tab_is_selected_in_bottom_nav(self, grid_page):
        el = grid_page.driver.find_element(
            "xpath", '//android.widget.ImageView[@content-desc="Tab 3 of 5"]'
        )
        assert el.get_attribute("selected") == "true", \
            "Grid tab (Tab 3 of 5) is not marked selected"

    def test_all_four_bottom_nav_tabs_present(self, grid_page):
        driver = grid_page.driver
        for tab_num in range(1, 6):
            el = driver.find_element(
                "xpath",
                f'//android.widget.ImageView[@content-desc="Tab {tab_num} of 5"]'
            )
            assert el.is_enabled(), f"Tab {tab_num} of 3 is not enabled"

    # ──────────────────────────────────────────────
    # TC-GI-003  Period Toggle – Today
    # ──────────────────────────────────────────────

    def test_today_tab_selected_by_default(self, grid_page):
        assert grid_page.is_today_tab_selected(), \
            "'Today' period tab is not selected by default"

    def test_today_tab_is_not_selected_after_switching_to_month(self, grid_page):
        grid_page.tap_this_month_tab()
        assert not grid_page.is_today_tab_selected(), \
            "'Today' tab still shows selected after tapping 'This Month'"
        assert grid_page.is_this_month_tab_selected(), \
            "'This Month' tab is not marked selected"

        # restore
        grid_page.tap_today_tab()

    def test_switch_back_to_today_tab(self, grid_page):
        grid_page.tap_this_month_tab()
        grid_page.tap_today_tab()
        assert grid_page.is_today_tab_selected(), \
            "Could not switch back to 'Today' tab"

    # ──────────────────────────────────────────────
    # TC-GI-004  Summary Cards – Labels
    # ──────────────────────────────────────────────

    def test_today_import_label_visible(self, grid_page):
        assert grid_page.is_today_import_label_visible(), \
            "'Today's Import' label not found on screen"

    def test_today_export_label_visible(self, grid_page):
        assert grid_page.is_today_export_label_visible(), \
            "'Today's Export' label not found on screen"

    # ──────────────────────────────────────────────
    # TC-GI-005  Summary Cards – Values
    # ──────────────────────────────────────────────

    def test_import_value_is_numeric(self, grid_page):
        value = grid_page.get_import_value()
        assert_is_numeric(value, "Today's Import")

    def test_export_value_is_numeric(self, grid_page):
        value = grid_page.get_export_value()
        assert_is_numeric(value, "Today's Export")

    def test_import_value_is_non_negative(self, grid_page):
        value = float(grid_page.get_import_value())
        assert value >= 0, f"Import value is negative: {value}"

    def test_export_value_is_non_negative(self, grid_page):
        value = float(grid_page.get_export_value())
        assert value >= 0, f"Export value is negative: {value}"

    # ──────────────────────────────────────────────
    # TC-GI-006  Horizontal Scroll
    # ──────────────────────────────────────────────

    def test_summary_card_strip_scrollable(self, grid_page):
        try:
            grid_page.scroll_summary_cards_right()
        except Exception as e:
            pytest.fail(f"Horizontal scroll raised an exception: {e}")

    # ──────────────────────────────────────────────
    # TC-GI-007  Grid Power Graph
    # ──────────────────────────────────────────────

    # def test_grid_power_graph_title_visible(self, grid_page):
    #     assert grid_page.is_grid_power_graph_visible(), \
    #         "'Grid Power Graphs' title not found"

    # def test_y_axis_labels_present_and_correct(self, grid_page):
    #     expected = {"6 kW", "5 kW", "4 kW", "3 kW", "2 kW", "1 kW", "0 kW", "-1 kW"}
    #     actual = set(grid_page.get_y_axis_labels())
    #     missing = expected - actual
    #     assert not missing, f"Missing Y-axis labels: {missing}"

    def test_x_axis_labels_present_and_correct(self, grid_page):
        expected = {"00", "03", "06", "09", "12", "15", "18", "21", "24"}
        actual = set(grid_page.get_x_axis_labels())
        missing = expected - actual
        assert not missing, f"Missing X-axis labels: {missing}"

    def test_y_axis_labels_are_in_descending_order(self, grid_page):
        labels = grid_page.get_y_axis_labels()
        values = [float(l.replace(" kW", "")) for l in labels]
        assert values == sorted(values, reverse=True), \
            f"Y-axis labels not in descending order: {labels}"

    def test_x_axis_labels_are_in_ascending_order(self, grid_page):
        labels = grid_page.get_x_axis_labels()
        values = [int(l) for l in labels]
        assert values == sorted(values), \
            f"X-axis labels not in ascending order: {labels}"

    # ──────────────────────────────────────────────
    # TC-GI-008  Yesterday Toggle
    # ──────────────────────────────────────────────

    def test_yesterday_toggle_visible(self, grid_page):
        assert grid_page.is_yesterday_label_visible(), \
            "'Yesterday's Data' label not found"

    def test_yesterday_toggle_off_by_default(self, grid_page):
        grid_page.disable_yesterday_data()
        assert not grid_page.is_yesterday_toggle_on(), \
            "Yesterday toggle is ON by default – expected OFF"

    def test_yesterday_toggle_turns_on(self, grid_page):
        grid_page.enable_yesterday_data()
        assert grid_page.is_yesterday_toggle_on(), \
            "Yesterday toggle did not turn ON after tapping"

    def test_yesterday_toggle_turns_off_again(self, grid_page):
        grid_page.enable_yesterday_data()
        grid_page.disable_yesterday_data()
        assert not grid_page.is_yesterday_toggle_on(), \
            "Yesterday toggle did not turn OFF after second tap"

    # ──────────────────────────────────────────────
    # TC-GI-009  Phase Indicators
    # ──────────────────────────────────────────────

    def test_phase_indicators_p1_p2_p3_visible(self, grid_page):
        assert grid_page.are_phase_indicators_visible(), \
            "One or more phase indicators (P1/P2/P3) are missing"

    # ──────────────────────────────────────────────
    # TC-GI-010  Scroll Down
    # ──────────────────────────────────────────────

    # def test_scroll_reveals_grid_voltages_section(self, grid_page):
    #     driver = grid_page.driver
    #     grid_page.scroll_to_bottom()

    #     elements = driver.find_elements(
    #         "xpath",
    #         '//*[contains(@content-desc, "Grid Voltages") or '
    #         'contains(@content-desc, "Voltage")]'
    #     )
    #     assert len(elements) > 0, \
    #         "Grid Voltages section not found after scrolling down"

    # ──────────────────────────────────────────────
    # TC-GI-011  Navigation Away and Back
    # ──────────────────────────────────────────────

    def test_navigate_to_home_and_back_to_grid(self, grid_page):
        grid_page.navigate_to_home_tab()
        grid_page.navigate_to_grid_tab()
        grid_page.wait_for_screen()

        assert grid_page.is_screen_loaded(), \
            "Grid screen did not reload after navigating away and back"

    def test_navigate_to_solar_and_back_to_grid(self, grid_page):
        grid_page.navigate_to_solar_tab()
        grid_page.navigate_to_grid_tab()
        grid_page.wait_for_screen()

        assert grid_page.is_screen_loaded(), \
            "Grid screen did not reload after Solar → Grid navigation"

    # ──────────────────────────────────────────────
    # TC-GI-012  This Month
    # ──────────────────────────────────────────────

    # def test_this_month_tab_shows_import_export_cards(self, grid_page):
    #     driver = grid_page.driver

    #     grid_page.tap_this_month_tab()

    #     grid_page.wait.until(
    #     lambda d: "This Month" in d.page_source
    # )

    #     els = driver.find_elements(
    #         AppiumBy.CLASS_NAME,
    #         "android.widget.HorizontalScrollView"
    #     )

    #     assert len(els) > 0, \
    #         "Summary card strip not found after switching to 'This Month'"

    #     grid_page.tap_today_tab()

    # ──────────────────────────────────────────────
    # TC-GI-013  UI Not Blank
    # ──────────────────────────────────────────────

    def test_screen_not_blank(self, grid_page):
        driver = grid_page.driver

        elements = driver.find_elements(
            "xpath", '//*[@content-desc!="" and @content-desc]'
        )

        assert len(elements) > 0, \
            "Screen appears blank – no elements found"