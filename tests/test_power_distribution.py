import pytest
from pages.power_distribution_page import PowerDistributionPage


class TestPowerDistribution:

    # ---------------- BASIC LOAD ----------------

    @pytest.mark.smoke
    def test_power_screen_loads(self, logged_in_driver):
        power = PowerDistributionPage(logged_in_driver)
        power.wait_for_screen()

        assert power.is_screen_loaded()
        print("✅ Screen loaded")


    # ---------------- CORE DATA ----------------

    @pytest.mark.smoke
    def test_power_values_exist(self, logged_in_driver):
        power = PowerDistributionPage(logged_in_driver)
        power.wait_for_screen()

        values = power.get_all_power_values()

        assert len(values) > 0
        print(f"✅ Power values: {values}")


    @pytest.mark.smoke
    def test_time_state_valid(self, logged_in_driver):
        power = PowerDistributionPage(logged_in_driver)
        power.wait_for_screen()

        state = power.get_time_state()

        assert state is not None
        assert state.lower() in ["producing", "consuming", "importing"]

        print(f"✅ State: {state}")


    # ---------------- EXPORT / IMPORT (SAFE VERSION) ----------------

    @pytest.mark.ui
    def test_export_import_labels_exist(self, logged_in_driver):
        power = PowerDistributionPage(logged_in_driver)
        power.wait_for_screen()

        assert power.is_export_visible()
        assert power.is_import_visible()

        print("✅ Export/Import labels visible")


    # ---------------- SYSTEM STATUS ----------------

    @pytest.mark.ui
    def test_system_status_visible(self, logged_in_driver):
        power = PowerDistributionPage(logged_in_driver)
        power.wait_for_screen()

        assert power.is_system_status_visible()
        print("✅ System status visible")