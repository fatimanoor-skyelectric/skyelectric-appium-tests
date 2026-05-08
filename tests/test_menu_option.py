import pytest
from pages.menu_option_page import MenuOptionsPage
import time


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def menu_page(driver):
    """
    Wraps the shared `driver` fixture from conftest.py.
    Navigates to the Menu Options screen via Tab 5 before each test,
    so every test starts from a known state.
    """
    page = MenuOptionsPage(driver)
    page.navigate()          # taps Tab 5 and waits for the header
    return page


# ── Test class ────────────────────────────────────────────────────────────────

class TestMenuOptionsScreen:
    """
    Basic smoke tests for the Menu Options screen.
    SmartFlow section is intentionally excluded from all cases.
    """

    # ── Screen load ───────────────────────────────────────────────────────────

    def test_menu_options_screen_is_loaded(self, menu_page):
        """The 'Menu Options' header must be visible after tapping Tab 5."""
        assert menu_page.is_loaded(), \
            "Menu Options screen did not load — header not found."

    # ── Individual item visibility ────────────────────────────────────────────

    def test_system_information_is_displayed(self, menu_page):
        assert menu_page.is_system_information_displayed(), \
            "'System Information' menu item is not displayed."

    def test_energy_saving_reports_is_displayed(self, menu_page):
        assert menu_page.is_energy_saving_reports_displayed(), \
            "'Energy Saving Reports' menu item is not displayed."

    def test_refer_a_friend_is_displayed(self, menu_page):
        assert menu_page.is_refer_a_friend_displayed(), \
            "'Refer a Friend' menu item is not displayed."

    def test_track_order_is_displayed(self, menu_page):
        assert menu_page.is_track_order_displayed(), \
            "'Track Order' menu item is not displayed."

    def test_policies_and_faqs_is_displayed(self, menu_page):
        assert menu_page.is_policies_and_faqs_displayed(), \
            "'Policies & FAQs' menu item is not displayed."

    def test_tutorials_and_updates_is_displayed(self, menu_page):
        assert menu_page.is_tutorials_and_updates_displayed(), \
            "'Tutorials & Updates' menu item is not displayed."

    def test_settings_is_displayed(self, menu_page):
        assert menu_page.is_settings_displayed(), \
            "'Settings' menu item is not displayed."

    # ── Bulk visibility (single sweep) ────────────────────────────────────────

    def test_all_menu_items_displayed(self, menu_page):
        """
        Verifies every expected menu item in one pass.
        Reports all missing items together so you don't have to re-run.
        """
        results = menu_page.all_menu_items_displayed()
        missing = [label for label, visible in results.items() if not visible]
        assert not missing, \
            f"The following menu items were NOT displayed: {missing}"

    # ── Clickability (parametrized) ───────────────────────────────────────────

    @pytest.mark.parametrize("attr, label", [
        ("SYSTEM_INFORMATION",    "System Information"),
        ("ENERGY_SAVING_REPORTS", "Energy Saving Reports"),
        ("REFER_A_FRIEND",        "Refer a Friend"),
        ("TRACK_ORDER",           "Track Order"),
        ("POLICIES_AND_FAQS",     "Policies & FAQs"),
        ("TUTORIALS_AND_UPDATES", "Tutorials & Updates"),
        ("SETTINGS",              "Settings"),
    ])
    def test_menu_item_is_clickable(self, menu_page, attr, label):
        """Confirms each tap target is ready without navigating away."""
        locator = getattr(MenuOptionsPage, attr)
        element = menu_page._find_clickable(locator)
        assert element is not None, f"'{label}' is not clickable."

    # ── Navigation smoke (tap → back → confirm return) ────────────────────────

    def test_tap_system_information_navigates(self, menu_page):
        menu_page.tap_system_information()
        # TODO: assert SystemInformationPage().is_loaded()
        menu_page.driver.back()
        time.sleep(1)
        assert menu_page.is_loaded(), \
            "Did not return to Menu Options after tapping System Information."

    def test_tap_energy_saving_reports_navigates(self, menu_page):
        menu_page.tap_energy_saving_reports()
        # TODO: assert EnergySavingReportsPage().is_loaded()
        menu_page.driver.back()
        time.sleep(2)
        assert menu_page.is_loaded(), \
            "Did not return to Menu Options after tapping Energy Saving Reports."

    # def test_tap_refer_a_friend_navigates(self, menu_page):
    #     menu_page.tap_refer_a_friend()
    #     # TODO: assert ReferAFriendPage().is_loaded()
    #     menu_page.driver.back()
    #     assert menu_page.is_loaded(), \
    #         "Did not return to Menu Options after tapping Refer a Friend."

    # def test_tap_track_order_navigates(self, menu_page):
    #     menu_page.tap_track_order()
    #     # TODO: assert TrackOrderPage().is_loaded()
    #     menu_page.driver.back()
    #     time.sleep(1)
    #     assert menu_page.is_loaded(), \
    #         "Did not return to Menu Options after tapping Track Order."

    def test_tap_policies_and_faqs_navigates(self, menu_page):
        menu_page.tap_policies_and_faqs()
        # TODO: assert PoliciesAndFAQsPage().is_loaded()
        menu_page.driver.back()
        time.sleep(1)
        assert menu_page.is_loaded(), \
            "Did not return to Menu Options after tapping Policies & FAQs."

    def test_tap_tutorials_and_updates_navigates(self, menu_page):
        menu_page.tap_tutorials_and_updates()
        # TODO: assert TutorialsAndUpdatesPage().is_loaded()
        menu_page.driver.back()
        time.sleep(1)
        assert menu_page.is_loaded(), \
            "Did not return to Menu Options after tapping Tutorials & Updates."

    def test_tap_settings_navigates(self, menu_page):
        menu_page.tap_settings()
        # TODO: assert SettingsPage().is_loaded()
        menu_page.driver.back()
        assert menu_page.is_loaded(), \
            "Did not return to Menu Options after tapping Settings."