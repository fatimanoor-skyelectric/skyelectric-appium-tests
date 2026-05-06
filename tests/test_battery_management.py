import pytest
from pages.battery_management_page import BatteryManagementPage


@pytest.fixture
def battery_page(driver):
    """Navigate to Battery Management (Tab 4) and return the page object."""
    page = BatteryManagementPage(driver)
    page.navigate_to_tab(4)
    return page


# ─────────────────────────────────────────────────────────────────────────────
# 1. Screen load
# ─────────────────────────────────────────────────────────────────────────────

class TestBatteryManagementScreenLoad:

    def test_battery_tab_is_active_on_open(self, battery_page):
        """Tab 4 must be selected when Battery Management screen opens."""
        active = battery_page.get_active_tab()
        assert active is not None, "No active tab found"
        assert active.get_attribute("selected") == "true"

    def test_soc_indicator_visible(self, battery_page):
        """Top-of-screen SOC indicator (100 %) should be displayed."""
        assert battery_page.get_soc_indicator().is_displayed()

    # def test_yesterday_label_visible_on_load(self, battery_page):
    #     """'Yesterday's Data' label must appear on screen after opening."""
    #     assert battery_page.is_yesterday_label_visible(), \
    #         "'Yesterday's Data' label not found on initial load"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Battery Usage Graph (above the fold)
# ─────────────────────────────────────────────────────────────────────────────

class TestBatteryUsageGraph:

    # def test_usage_graph_y_axis_labels_count(self, battery_page):
    #     labels = battery_page.get_usage_graph_y_labels()

    #     assert len(labels) >= 2, \
    #         f"Expected at least 2 Y-axis labels, found {len(labels)}"

    def test_usage_graph_x_axis_labels_count(self, battery_page):
        """All nine X-axis hour labels (00–24) must be visible."""
        labels = battery_page.get_usage_graph_x_labels()
        assert len(labels) == 9, \
            f"Expected 9 X-axis labels, found {len(labels)}"

    @pytest.mark.parametrize("locator_name,expected_desc", [
        ("USAGE_Y_1KW",    "1 kW"),
        ("USAGE_Y_0KW",    "0 kW"),
        ("USAGE_Y_NEG1KW", "-1 kW"),
    ])
    def test_usage_y_axis_label_present(self, battery_page, locator_name, expected_desc):
        """Each Y-axis kW label is individually present."""
        loc = getattr(battery_page, locator_name)
        el  = battery_page._find(loc)
        assert el is not None, f"Usage graph Y-axis label '{expected_desc}' not found"

    @pytest.mark.parametrize("locator_name,expected_desc", [
        ("USAGE_X_00", "00"),
        ("USAGE_X_06", "06"),
        ("USAGE_X_12", "12"),
        ("USAGE_X_18", "18"),
        ("USAGE_X_24", "24"),
    ])
    def test_usage_x_axis_key_labels_present(self, battery_page, locator_name, expected_desc):
        """Spot-check key X-axis hour labels on the Usage graph."""
        loc = getattr(battery_page, locator_name)
        el  = battery_page._find(loc)
        assert el is not None, f"Usage graph X-axis label '{expected_desc}' not found"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Yesterday's Data toggle — Usage Graph (toggle 1 / instance 0)
# ─────────────────────────────────────────────────────────────────────────────

class TestUsageGraphYesterdayToggle:

    def test_usage_toggle_off_by_default(self, battery_page):
        """Usage graph Yesterday's Data switch must be OFF on screen load."""
        assert not battery_page.is_usage_yesterday_toggle_on(), \
            "Usage toggle should be OFF by default"

    def test_usage_toggle_turns_on(self, battery_page):
        """Tapping the Usage toggle once must enable it."""
        battery_page.tap_usage_yesterday_toggle()
        assert battery_page.is_usage_yesterday_toggle_on(), \
            "Usage toggle did not turn ON after tap"

    # def test_usage_toggle_turns_off_again(self, battery_page):
    #     """Tapping the Usage toggle twice must return it to OFF."""
    #     battery_page.tap_usage_yesterday_toggle()  # → ON
    #     battery_page.tap_usage_yesterday_toggle()  # → OFF
    #     assert not battery_page.is_usage_yesterday_toggle_on(), \
    #         "Usage toggle did not return to OFF after second tap"

    def test_soc_toggle_unaffected_by_usage_toggle(self, battery_page):
        """Toggling the Usage switch must not change the SOC graph switch."""
        battery_page.scroll_to_soc_graph()
        soc_state_before = battery_page.is_soc_yesterday_toggle_on()

        battery_page.tap_usage_yesterday_toggle()
        soc_state_after = battery_page.is_soc_yesterday_toggle_on()

        assert soc_state_before == soc_state_after, \
            "SOC toggle state changed when only the Usage toggle was tapped"

        # restore
        battery_page.tap_usage_yesterday_toggle()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Battery SOC Graph (below the fold — requires scroll)
# ─────────────────────────────────────────────────────────────────────────────

class TestBatterySOCGraph:

    @pytest.fixture(autouse=True)
    def scroll_to_soc(self, battery_page):
        """Scroll to SOC graph before every test in this class."""
        battery_page.scroll_to_soc_graph()

    def test_soc_graph_header_visible(self, battery_page):
        """'Battery SOC Graph' heading must be visible after scrolling."""
        assert battery_page.is_soc_graph_header_visible(), \
            "'Battery SOC Graph' header not visible after scroll"

    def test_soc_graph_y_axis_label_count(self, battery_page):
        """All six Y-axis % labels (0 %–100 %) must be visible."""
        labels = battery_page.get_soc_graph_y_labels()
        assert len(labels) == 6, \
            f"Expected 6 SOC Y-axis labels, found {len(labels)}"

    @pytest.mark.parametrize("locator_name,expected_desc", [
        ("SOC_Y_100", "100 %"),
        ("SOC_Y_80",  "80 %"),
        ("SOC_Y_60",  "60 %"),
        ("SOC_Y_40",  "40 %"),
        ("SOC_Y_20",  "20 %"),
        ("SOC_Y_0",   "0 %"),
    ])
    def test_soc_y_axis_individual_labels(self, battery_page, locator_name, expected_desc):
        """Each SOC graph Y-axis label is individually present."""
        loc = getattr(battery_page, locator_name)
        el  = battery_page._find(loc)
        assert el is not None, f"SOC graph Y-axis label '{expected_desc}' not found"

    def test_soc_graph_x_axis_label_count(self, battery_page):
        """All nine X-axis hour labels (00–24) must be visible on SOC graph."""
        labels = battery_page.get_soc_graph_x_labels()
        assert len(labels) == 9, \
            f"Expected 9 SOC X-axis labels, found {len(labels)}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Yesterday's Data toggle — SOC Graph (toggle 2 / instance 1)
# ─────────────────────────────────────────────────────────────────────────────

class TestSOCGraphYesterdayToggle:

    @pytest.fixture(autouse=True)
    def scroll_to_soc(self, battery_page):
        battery_page.scroll_to_soc_graph()

    def test_soc_toggle_off_by_default(self, battery_page):
        """SOC graph Yesterday's Data switch must be OFF on screen load."""
        assert not battery_page.is_soc_yesterday_toggle_on(), \
            "SOC toggle should be OFF by default"

    def test_soc_toggle_turns_on(self, battery_page):
        """Tapping the SOC toggle once must enable it."""
        battery_page.tap_soc_yesterday_toggle()
        assert battery_page.is_soc_yesterday_toggle_on(), \
            "SOC toggle did not turn ON after tap"

    # def test_soc_toggle_turns_off_again(self, battery_page):
    #     """Tapping the SOC toggle twice must return it to OFF."""
    #     battery_page.tap_soc_yesterday_toggle()  # → ON
    #     battery_page.tap_soc_yesterday_toggle()  # → OFF
    #     assert not battery_page.is_soc_yesterday_toggle_on(), \
    #         "SOC toggle did not return to OFF after second tap"

    def test_usage_toggle_unaffected_by_soc_toggle(self, battery_page):
        """Toggling the SOC switch must not change the Usage graph switch."""
        usage_state_before = battery_page.is_usage_yesterday_toggle_on()

        battery_page.tap_soc_yesterday_toggle()
        usage_state_after = battery_page.is_usage_yesterday_toggle_on()

        assert usage_state_before == usage_state_after, \
            "Usage toggle state changed when only the SOC toggle was tapped"

        # restore
        battery_page.tap_soc_yesterday_toggle()


# ─────────────────────────────────────────────────────────────────────────────
# 6. Bottom navigation
# ─────────────────────────────────────────────────────────────────────────────

class TestBottomNavigation:

    @pytest.mark.parametrize("tab_num", [1, 2, 3, 5])
    def test_navigate_away_from_battery_tab(self, battery_page, tab_num):
        """Tapping any other tab should deselect the Battery tab."""
        battery_page.navigate_to_tab(tab_num)
        active = battery_page.get_active_tab()
        assert active is not None, \
            f"No active tab found after navigating to tab {tab_num}"
        assert active.get_attribute("content-desc") == f"Tab {tab_num} of 5", \
            f"Expected Tab {tab_num} to be active"

    def test_return_to_battery_tab(self, battery_page):
        """Navigating away and back to Tab 4 should re-activate it."""
        battery_page.navigate_to_tab(1)
        battery_page.navigate_to_tab(4)
        active = battery_page.get_active_tab()
        assert active is not None
        assert active.get_attribute("content-desc") == "Tab 4 of 5", \
            "Battery tab (Tab 4) is not active after returning to it"