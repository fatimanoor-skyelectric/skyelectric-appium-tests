"""
Test suite for the Battery Management screen (full scroll).
Covers: battery card, stats row, Battery Usage Graph, Battery SOC Graph,
        Yesterday's Data toggles, and bottom navigation.

Run:
    pytest tests/test_battery_management.py -v
"""

import re
import pytest
from appium import webdriver
from appium.options import UiAutomator2Options

from battery_management_page import BatteryManagementPage


# ── Appium capabilities ────────────────────────────────────────────────────────
CAPABILITIES = {
    "platformName":                "Android",
    "appium:automationName":       "UiAutomator2",
    "appium:deviceName":           "Android Device",
    "appium:appPackage":           "com.skyelectric.smartapp",
    "appium:appActivity":          ".MainActivity",
    "appium:noReset":              True,
    "appium:autoGrantPermissions": True,
}

APPIUM_SERVER_URL = "http://127.0.0.1:4723"


# ── Session fixture ────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """Start one Appium session for the entire module."""
    options = UiAutomator2Options().load_capabilities(CAPABILITIES)
    _driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    _driver.implicitly_wait(0)          # rely on explicit waits only
    yield _driver
    _driver.quit()


@pytest.fixture(scope="module")
def battery_page(driver):
    """
    Navigate to the Battery Management tab and return the page object.
    Assumes the app is already on an authenticated screen after launch.
    """
    page = BatteryManagementPage(driver)
    page.tap_tab(BatteryManagementPage.TAB_BATTERY)
    return page


# ══════════════════════════════════════════════════════════════════════════════
# Test class
# ══════════════════════════════════════════════════════════════════════════════
class TestBatteryManagementScreen:

    # ── 1. Screen load ─────────────────────────────────────────────────────────
    def test_screen_loads_successfully(self, battery_page):
        """Battery Management title must appear after tapping the battery tab."""
        assert battery_page.is_loaded(), (
            "Battery Management screen did not load within the expected timeout."
        )

    # ── 2. Battery status card ─────────────────────────────────────────────────
    def test_battery_percentage_is_visible(self, battery_page):
        pct = battery_page.get_battery_percentage()
        assert pct, "Battery percentage element is empty or not found."

    def test_battery_percentage_format(self, battery_page):
        pct = battery_page.get_battery_percentage()
        assert re.match(r"^\d+%$", pct), (
            f"Battery percentage '{pct}' does not match expected '\\d+%' format."
        )

    def test_battery_percentage_valid_range(self, battery_page):
        pct   = battery_page.get_battery_percentage()
        value = int(pct.replace("%", ""))
        assert 0 <= value <= 100, (
            f"Battery percentage {value}% is outside valid range [0, 100]."
        )

    # ── 3. Stats row ───────────────────────────────────────────────────────────
    def test_current_load_label_visible(self, battery_page):
        assert battery_page._is_visible(BatteryManagementPage.STAT_LABEL_CURRENT_LOAD), (
            "'At Current Load' label is not visible."
        )

    def test_stored_power_label_visible(self, battery_page):
        assert battery_page._is_visible(BatteryManagementPage.STAT_LABEL_STORED_POWER), (
            "'Stored Power' label is not visible."
        )

    def test_hrs_unit_label_visible(self, battery_page):
        assert battery_page._is_visible(BatteryManagementPage.STAT_VALUE_HRS), (
            "'Hrs' unit label is not visible."
        )

    def test_units_label_visible(self, battery_page):
        assert battery_page._is_visible(BatteryManagementPage.STAT_VALUE_UNITS), (
            "'Units' label is not visible."
        )

    def test_current_load_value_format(self, battery_page):
        value = battery_page.get_current_load_value()
        assert value, "Current Load value is empty."
        assert re.match(r"^\d{2}:\d{2}$", value), (
            f"Current Load value '{value}' does not match HH:MM format."
        )

    def test_stored_power_value_is_numeric(self, battery_page):
        value = battery_page.get_stored_power_value()
        assert value, "Stored Power value is empty."
        assert re.match(r"^\d+(\.\d+)?$", value), (
            f"Stored Power value '{value}' is not a valid decimal number."
        )

    # ── 4. Battery Usage Graph ─────────────────────────────────────────────────
    def test_usage_graph_title_visible(self, battery_page):
        assert battery_page.is_usage_graph_visible(), (
            "'Battery Usage Graph' title is not visible."
        )

    def test_usage_y_axis_all_labels_present(self, battery_page):
        expected = set(BatteryManagementPage.USAGE_Y_AXIS_LABELS_ORDERED)
        visible  = set(battery_page.get_usage_y_axis_labels())
        missing  = expected - visible
        assert not missing, f"Missing Usage Graph Y-axis labels: {missing}"

    def test_usage_y_axis_labels_in_order(self, battery_page):
        labels = battery_page.get_usage_y_axis_labels()
        assert labels == BatteryManagementPage.USAGE_Y_AXIS_LABELS_ORDERED, (
            f"Usage Graph Y-axis labels out of order. Got: {labels}"
        )

    def test_usage_x_axis_all_labels_present(self, battery_page):
        expected = set(BatteryManagementPage.X_AXIS_VALUES)
        visible  = set(battery_page.get_usage_x_axis_labels())
        missing  = expected - visible
        assert not missing, f"Missing Usage Graph X-axis labels: {missing}"

    # ── 5. Yesterday's Data toggle – Usage Graph ───────────────────────────────
    def test_usage_yesterday_label_visible(self, battery_page):
        """'Yesterday's Data' label must appear next to the Usage Graph toggle."""
        assert battery_page.is_yesterday_label_visible(), (
            "'Yesterday's Data' label is not visible near the Usage Graph."
        )

    def test_usage_yesterday_toggle_default_off(self, battery_page):
        """Yesterday's Data toggle should be OFF (unchecked) by default."""
        assert not battery_page.get_usage_yesterday_toggle_state(), (
            "Usage Graph 'Yesterday's Data' toggle should be OFF by default."
        )

    def test_usage_yesterday_toggle_turns_on(self, battery_page):
        """Tapping the toggle should switch it from OFF to ON."""
        battery_page.toggle_usage_yesterday_data()
        assert battery_page.get_usage_yesterday_toggle_state(), (
            "Usage Graph toggle did not turn ON after tap."
        )

    def test_usage_yesterday_toggle_turns_off_again(self, battery_page):
        """Tapping the toggle a second time should revert it to OFF."""
        battery_page.toggle_usage_yesterday_data()
        assert not battery_page.get_usage_yesterday_toggle_state(), (
            "Usage Graph toggle did not turn OFF after second tap."
        )

    # ── 6. Battery SOC Graph (scroll required) ─────────────────────────────────
    def test_soc_graph_visible_after_scroll(self, battery_page):
        """Battery SOC Graph must become visible after scrolling down."""
        battery_page.scroll_to_soc_graph()
        assert battery_page.is_soc_graph_visible(), (
            "'Battery SOC Graph' title is not visible after scrolling."
        )

    def test_soc_y_axis_all_labels_present(self, battery_page):
        expected = set(BatteryManagementPage.SOC_Y_AXIS_LABELS_ORDERED)
        visible  = set(battery_page.get_soc_y_axis_labels())
        missing  = expected - visible
        assert not missing, f"Missing SOC Graph Y-axis labels: {missing}"

    def test_soc_y_axis_labels_in_order(self, battery_page):
        labels = battery_page.get_soc_y_axis_labels()
        assert labels == BatteryManagementPage.SOC_Y_AXIS_LABELS_ORDERED, (
            f"SOC Graph Y-axis labels out of order. Got: {labels}"
        )

    def test_soc_x_axis_all_labels_present(self, battery_page):
        expected = set(BatteryManagementPage.X_AXIS_VALUES)
        visible  = set(battery_page.get_soc_x_axis_labels())
        missing  = expected - visible
        assert not missing, f"Missing SOC Graph X-axis labels: {missing}"

    def test_soc_y_axis_values_are_percentages(self, battery_page):
        """Every SOC Y-axis label must end with ' %' and have a numeric prefix."""
        for label in battery_page.get_soc_y_axis_labels():
            assert re.match(r"^\d+ %$", label), (
                f"SOC Y-axis label '{label}' does not match '\\d+ %' format."
            )

    def test_soc_y_axis_range_is_0_to_100(self, battery_page):
        """SOC Y-axis values must span 0 % to 100 % in 20 % increments."""
        labels   = battery_page.get_soc_y_axis_labels()
        values   = [int(lbl.replace(" %", "")) for lbl in labels]
        expected = [100, 80, 60, 40, 20, 0]
        assert values == expected, (
            f"SOC Y-axis values are incorrect. Got: {values}, expected: {expected}"
        )

    # ── 7. Yesterday's Data toggle – SOC Graph ─────────────────────────────────
    def test_soc_yesterday_toggle_default_off(self, battery_page):
        """SOC Graph Yesterday's Data toggle should be OFF by default."""
        assert not battery_page.get_soc_yesterday_toggle_state(), (
            "SOC Graph 'Yesterday's Data' toggle should be OFF by default."
        )

    def test_soc_yesterday_toggle_turns_on(self, battery_page):
        """Tapping the SOC toggle should switch it to ON."""
        battery_page.toggle_soc_yesterday_data()
        assert battery_page.get_soc_yesterday_toggle_state(), (
            "SOC Graph toggle did not turn ON after tap."
        )

    def test_soc_yesterday_toggle_turns_off_again(self, battery_page):
        """Tapping the SOC toggle a second time should revert it to OFF."""
        battery_page.toggle_soc_yesterday_data()
        assert not battery_page.get_soc_yesterday_toggle_state(), (
            "SOC Graph toggle did not turn OFF after second tap."
        )

    def test_two_toggles_are_independent(self, battery_page):
        """Toggling Usage Graph switch must not affect the SOC Graph switch."""
        # Ensure both start OFF
        if battery_page.get_usage_yesterday_toggle_state():
            battery_page.toggle_usage_yesterday_data()
        if battery_page.get_soc_yesterday_toggle_state():
            battery_page.toggle_soc_yesterday_data()

        # Turn ON only the Usage Graph toggle
        battery_page.toggle_usage_yesterday_data()

        assert battery_page.get_usage_yesterday_toggle_state(), (
            "Usage Graph toggle should be ON."
        )
        assert not battery_page.get_soc_yesterday_toggle_state(), (
            "SOC Graph toggle should remain OFF when only Usage toggle is tapped."
        )

        # Clean up
        battery_page.toggle_usage_yesterday_data()

    # ── 8. Bottom navigation ───────────────────────────────────────────────────
    def test_battery_tab_is_selected(self, battery_page):
        assert battery_page.is_battery_tab_selected(), (
            "Tab 4 of 5 (Battery) is not marked selected on Battery Management screen."
        )

    def test_all_five_tabs_present(self, battery_page):
        tabs = [
            BatteryManagementPage.TAB_HOME,
            BatteryManagementPage.TAB_ENERGY,
            BatteryManagementPage.TAB_GRID,
            BatteryManagementPage.TAB_BATTERY,
            BatteryManagementPage.TAB_MORE,
        ]
        for tab in tabs:
            assert battery_page._is_visible(tab, timeout=5), (
                f"Tab '{tab[1]}' is not visible in the bottom navigation bar."
            )

    def test_navigate_away_and_return_reloads_screen(self, driver, battery_page):
        """Leaving to another tab and returning should show Battery Management again."""
        battery_page.navigate_to_home()
        driver.implicitly_wait(2)

        battery_page.tap_tab(BatteryManagementPage.TAB_BATTERY)
        driver.implicitly_wait(0)

        assert battery_page.is_loaded(), (
            "Battery Management screen did not reload after navigating away and back."
        )