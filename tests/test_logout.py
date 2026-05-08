import pytest
from pages.logout_page import LogoutPage


# --------------------------------------------------------------------------- #
#  Fixture                                                                     #
# --------------------------------------------------------------------------- #
@pytest.fixture
def logout_page(driver):
    """Return a LogoutPage instance bound to the active driver session."""
    return LogoutPage(driver)


@pytest.fixture
def at_logout_dialog(logout_page):
    """
    Navigate all the way to the logout confirmation dialog and return the
    LogoutPage so tests can interact with it immediately.

    Path: Menu tab → Profile icon → Profile screen → Logout icon → dialog.
    """
    logout_page.navigate_to_logout_dialog()
    return logout_page


# --------------------------------------------------------------------------- #
#  Tests                                                                       #
# --------------------------------------------------------------------------- #
class TestLogoutFlow:

    # ── Dialog appearance ──────────────────────────────────────────────────

    def test_logout_dialog_appears_after_tapping_logout_icon(self, at_logout_dialog):
        """Dialog must be visible after tapping the Logout icon on Profile."""
        assert at_logout_dialog.is_logout_dialog_visible(), (
            "Logout confirmation dialog did not appear after tapping Logout icon."
        )

    def test_dialog_title_is_logout(self, at_logout_dialog):
        """Dialog title content-desc should read exactly 'Logout'."""
        assert at_logout_dialog.get_dialog_title() == "Logout", (
            "Dialog title text is incorrect."
        )

    def test_dialog_message_is_correct(self, at_logout_dialog):
        """Dialog body should display the expected confirmation message."""
        expected = "Are you sure you want to logout?"
        assert at_logout_dialog.get_dialog_message() == expected, (
            f"Dialog message mismatch. Expected: '{expected}'"
        )

    # ── Cancel path ────────────────────────────────────────────────────────

    def test_cancel_dismisses_dialog(self, at_logout_dialog):
        """Tapping Cancel must close the dialog."""
        at_logout_dialog.cancel_logout()

        assert not at_logout_dialog.is_logout_dialog_visible(), (
            "Dialog still visible after tapping Cancel."
        )

    def test_cancel_keeps_user_on_profile_screen(self, at_logout_dialog):
        """After Cancel the user must remain on the Profile screen."""
        at_logout_dialog.cancel_logout()

        assert at_logout_dialog.is_on_profile_screen(), (
            "Profile screen not visible after tapping Cancel."
        )

    # ── Logout path ────────────────────────────────────────────────────────

    def test_confirm_logout_navigates_to_login_screen(self, at_logout_dialog):
        """Confirming logout must redirect the user to the Login screen."""
        at_logout_dialog.confirm_logout()

        assert at_logout_dialog.is_on_login_screen(), (
            "Login screen not visible after confirming logout."
        )

    # def test_dialog_gone_after_confirming_logout(self, at_logout_dialog):
    #     """Dialog must not remain on screen after logout is confirmed."""
    #     at_logout_dialog.confirm_logout()

    #     assert not at_logout_dialog.is_logout_dialog_visible(), (
    #         "Dialog still visible after logout was confirmed."
    #     )

    # ── Full composed flow ─────────────────────────────────────────────────

    # def test_full_logout_flow(self, logout_page):
    #     """
    #     End-to-end smoke: start from wherever the driver lands after login
    #     and verify the app reaches the Login screen after a full logout.
    #     """
    #     logout_page.logout()

    #     assert logout_page.is_on_login_screen(), (
    #         "App did not reach Login screen after full logout flow."
    #     )

    # def test_full_cancel_flow_stays_logged_in(self, logout_page):
    #     """
    #     End-to-end negative path: navigate to dialog, cancel, confirm the
    #     user is still authenticated on the Profile screen.
    #     """
    #     logout_page.logout_and_cancel()

    #     assert logout_page.is_on_profile_screen(), (
    #         "User is not on Profile screen after cancelling logout."
    #     )