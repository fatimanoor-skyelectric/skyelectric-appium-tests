from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

logger = logging.getLogger(__name__)


class LogoutPage:
    """
    Page Object for the full Logout flow.

    Flow:
        1. Tap the Menu tab (Tab 5 of 5) in the bottom navigation bar.
        2. Tap the Profile icon via coordinates (NAF element, no content-desc).
        3. Wait for the Profile Details screen to load.
        4. Tap the Logout icon (top-right of the profile screen).
        5. Interact with the Logout / Cancel confirmation dialog.

    Dialog outcomes:
        - tap_confirm_logout()  → logs out, navigates to Login screen.
        - tap_cancel_logout()   → dismisses dialog, returns to Profile screen.
    """

    DEFAULT_TIMEOUT = 15

    # ------------------------------------------------------------------ #
    #  Profile icon coordinates                                           #
    #  NAF element, no content-desc — tap centre of bounds               #
    #  [949,206][1037,294]                                                #
    # ------------------------------------------------------------------ #
    PROFILE_ICON_X = 993   # (949 + 1037) // 2
    PROFILE_ICON_Y = 250   # (206 + 294)  // 2

    # ------------------------------------------------------------------ #
    #  Bottom Navigation                                                  #
    # ------------------------------------------------------------------ #
    MENU_TAB = (
        AppiumBy.XPATH,
        '//android.widget.ImageView[@content-desc="Tab 5 of 5"]',
    )

    # ------------------------------------------------------------------ #
    #  Profile Details Screen                                             #
    # ------------------------------------------------------------------ #
    PROFILE_SCREEN_INDICATOR = (
        AppiumBy.XPATH,
        '//android.view.View[@content-desc="Logout"]',
    )

    LOGOUT_ICON = (
        AppiumBy.XPATH,
        '//android.widget.ImageView[@content-desc="Logout"]',
    )

    # ------------------------------------------------------------------ #
    #  Logout Confirmation Dialog                                         #
    # ------------------------------------------------------------------ #

    # Non-clickable View — dialog title
    LOGOUT_DIALOG_TITLE = (
        AppiumBy.XPATH,
        '//android.view.View[@content-desc="Logout" and @clickable="false"]',
    )

    # Confirmation message
    LOGOUT_DIALOG_MESSAGE = (
        AppiumBy.XPATH,
        '//android.view.View[@content-desc="Are you sure you want to logout?"]',
    )

    # Clickable Button — confirms logout
    LOGOUT_CONFIRM_BUTTON = (
        AppiumBy.XPATH,
        '//android.widget.Button[@content-desc="Logout"]',
    )

    # Clickable Button — dismisses dialog
    CANCEL_BUTTON = (
        AppiumBy.XPATH,
        '//android.widget.Button[@content-desc="Cancel"]',
    )

    # ------------------------------------------------------------------ #
    #  Destination screen indicators (for post-action assertions)         #
    # ------------------------------------------------------------------ #

    # Adjust content-desc to match a reliable landmark on your Login screen
    LOGIN_SCREEN_INDICATOR = (
    AppiumBy.XPATH,
    '//android.widget.Button[@content-desc="Login"]',
)

    # ------------------------------------------------------------------ #
    #  Constructor                                                        #
    # ------------------------------------------------------------------ #
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    # ------------------------------------------------------------------ #
    #  Private helpers                                                    #
    # ------------------------------------------------------------------ #
    def _find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def _click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logger.info("Clicked element: %s", locator)
        return element

    def _tap_by_coordinates(self, x, y):
        """Tap a NAF element with no content-desc by absolute coordinates."""
        self.driver.tap([(x, y)])
        logger.info("Tapped coordinates (%s, %s)", x, y)

    def _is_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def _get_content_desc(self, locator):
        return self._find(locator).get_attribute("content-desc")

    # ------------------------------------------------------------------ #
    #  Navigation steps                                                   #
    # ------------------------------------------------------------------ #
    def tap_menu_tab(self):
        """Tap the Menu tab safely."""

        logger.info("Trying to tap Menu tab")

        elements = self.driver.find_elements(*self.MENU_TAB)

        if not elements:
            raise Exception(
                "Menu tab not found. Current screen may not contain bottom navigation."
            )

        elements[0].click()

        logger.info("Menu tab clicked")

    def tap_profile_icon(self):
        """
        Tap the Profile icon via coordinates.
        Element is NAF with no content-desc — tap centre of [949,206][1037,294].
        """
        logger.info("Tapping Profile icon via coordinates (%s, %s)",
                    self.PROFILE_ICON_X, self.PROFILE_ICON_Y)
        self._tap_by_coordinates(self.PROFILE_ICON_X, self.PROFILE_ICON_Y)

    def wait_for_profile_screen(self):
        """Wait until the Profile Details screen is fully loaded."""
        logger.info("Waiting for Profile Details screen")
        self.wait.until(EC.presence_of_element_located(self.PROFILE_SCREEN_INDICATOR))
        logger.info("Profile screen loaded")

    def tap_logout_icon(self):
        """Tap the Logout icon on the top-right of the Profile screen."""
        logger.info("Tapping Logout icon")
        self._click(self.LOGOUT_ICON)

    # ------------------------------------------------------------------ #
    #  Dialog state queries                                               #
    # ------------------------------------------------------------------ #
    def is_logout_dialog_visible(self) -> bool:
        """Return True if the logout confirmation dialog is currently visible."""
        return self._is_visible(self.LOGOUT_CONFIRM_BUTTON)

    def get_dialog_title(self) -> str:
        """Return the content-desc of the dialog title element."""
        return self._get_content_desc(self.LOGOUT_DIALOG_TITLE)

    def get_dialog_message(self) -> str:
        """Return the confirmation message shown in the dialog."""
        return self._get_content_desc(self.LOGOUT_DIALOG_MESSAGE)

    # ------------------------------------------------------------------ #
    #  Dialog actions                                                     #
    # ------------------------------------------------------------------ #
    def wait_for_logout_dialog(self):
        """Wait until the logout confirmation dialog is displayed."""
        logger.info("Waiting for logout confirmation dialog")
        self.wait.until(EC.presence_of_element_located(self.LOGOUT_CONFIRM_BUTTON))
        logger.info("Logout dialog appeared")

    def confirm_logout(self):
        """
        Tap the 'Logout' button and wait until Login screen appears.
        """
        logger.info("Confirming logout")

        confirm_btn = self.wait.until(
            EC.element_to_be_clickable(self.LOGOUT_CONFIRM_BUTTON)
        )
        confirm_btn.click()

        logger.info("Waiting for Login screen after logout")

        self.wait.until(
            EC.presence_of_element_located(self.LOGIN_SCREEN_INDICATOR)
        )

        logger.info("Successfully navigated to Login screen")


    def cancel_logout(self):
        """
        Tap the 'Cancel' button and wait until dialog disappears.
        """
        logger.info("Cancelling logout")

        cancel_btn = self.wait.until(
            EC.element_to_be_clickable(self.CANCEL_BUTTON)
        )

        cancel_btn.click()

        logger.info("Waiting for dialog to disappear")

        self.wait.until_not(
            EC.presence_of_element_located(self.LOGOUT_CONFIRM_BUTTON)
        )
        logger.info("Waiting for Profile screen to remain visible")

        self.wait.until(
            EC.presence_of_element_located(self.PROFILE_SCREEN_INDICATOR)
        )

        logger.info("Logout cancelled successfully")

    # ------------------------------------------------------------------ #
    #  Destination checks (used in tests after dialog interaction)        #
    # ------------------------------------------------------------------ #
    def is_on_login_screen(self) -> bool:
        """Return True when the Login screen is visible (post-logout)."""
        return self._is_visible(self.LOGIN_SCREEN_INDICATOR)

    def is_on_profile_screen(self) -> bool:
        """Return True when the Profile screen is visible (post-cancel)."""
        return self._is_visible(self.PROFILE_SCREEN_INDICATOR)

    # ------------------------------------------------------------------ #
    #  High-level composed flows                                          #
    # ------------------------------------------------------------------ #
    def navigate_to_logout_dialog(self):
        """
        Robust navigation to logout dialog.

        Handles:
            - Already on dialog
            - Already on profile screen
            - Starting from dashboard/home
            - Flutter transition delays
        """

        logger.info("Navigating to logout dialog")

        # -------------------------------------------------------------- #
        # Already on dialog
        # -------------------------------------------------------------- #
        if self.is_logout_dialog_visible():
            logger.info("Logout dialog already visible")
            return

        # -------------------------------------------------------------- #
        # Already on Profile screen
        # -------------------------------------------------------------- #
        if self.is_on_profile_screen():
            logger.info("Already on Profile screen")

            self.tap_logout_icon()
            self.wait_for_logout_dialog()
            return

        # -------------------------------------------------------------- #
        # Try Menu → Profile flow
        # -------------------------------------------------------------- #

        logger.info("Opening Menu tab")

        menu_elements = self.driver.find_elements(*self.MENU_TAB)

        if menu_elements:
            menu_elements[0].click()
            logger.info("Menu tab clicked")
        else:
            raise Exception(
                "MENU_TAB not found. App is probably on Login screen "
                "or unexpected state."
            )

        # Flutter animation stabilization
        self.driver.implicitly_wait(1)

        logger.info("Opening Profile screen")

        self.tap_profile_icon()

        self.wait_for_profile_screen()

        logger.info("Opening Logout dialog")

        self.tap_logout_icon()

        self.wait_for_logout_dialog()

    def logout(self):
        """
        Full logout flow ending with confirmation.
            Menu tab → Profile icon → Profile screen → Logout icon → Confirm.
        """
        self.navigate_to_logout_dialog()
        self.confirm_logout()
        logger.info("Logout completed successfully")

    def logout_and_cancel(self):
        """
        Navigate to the logout dialog then dismiss it with Cancel.
        User remains logged in on the Profile screen.
        """
        self.navigate_to_logout_dialog()
        self.cancel_logout()
        logger.info("Logout cancelled — user remains logged in")