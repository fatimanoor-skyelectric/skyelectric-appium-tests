"""
Page Object Model – Battery Management Screen
App Package : com.skyelectric.smartapp
Automation  : Appium 2.x + UiAutomator2
Python      : 3.9+

Locator Strategy Notes
──────────────────────
• Tuples follow the Selenium/Appium convention: (By, value)
• AppiumBy.ACCESSIBILITY_ID  →  content-desc attribute  (React Native accessibilityLabel)
• AppiumBy.ID                →  fully-qualified resource-id
• AppiumBy.XPATH             →  XPath expression (last resort)
• AppiumBy.ANDROID_UIAUTOMATOR → raw UiAutomator2 selector (scrolling, complex lookups)

Adjust locator values to match what you see in Appium Inspector / UIAutomatorViewer.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# ── Timing constants (seconds) ──────────────────────────────────────────────
DEFAULT_TIMEOUT  = 10
SHORT_TIMEOUT    = 5
POLL_FREQUENCY   = 0.3

# ── App package prefix (avoid repetition) ───────────────────────────────────
_PKG = "com.skyelectric.smartapp"


class BatteryManagementPage:
    """
    Encapsulates all locators and interactions for the Battery Management screen.

    Usage
    ─────
    page = BatteryManagementPage(driver)
    page.tap_tab(BatteryManagementPage.TAB_BATTERY)
    assert page.is_loaded()
    """

    # ══════════════════════════════════════════════════════════════════════════
    # ── Locator constants ─────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    # Bottom navigation tabs
    # content-desc values are whatever accessibilityLabel the RN app exposes.
    # Verify in Appium Inspector; common patterns shown below.
    TAB_HOME    = (AppiumBy.ACCESSIBILITY_ID, "Home")
    TAB_ENERGY  = (AppiumBy.ACCESSIBILITY_ID, "Energy")
    TAB_GRID    = (AppiumBy.ACCESSIBILITY_ID, "Grid")
    TAB_BATTERY = (AppiumBy.ACCESSIBILITY_ID, "Battery")
    TAB_MORE    = (AppiumBy.ACCESSIBILITY_ID, "More")

    # Screen title (confirms the screen has loaded)
    SCREEN_TITLE = (
        AppiumBy.XPATH,
        '//*[@text="Battery Management" or @content-desc="Battery Management"]',
    )

    # Battery status card
    # The percentage element usually has an accessibility label like "75%" or
    # resource-id ending in "batteryPercentage".
    BATTERY_PERCENTAGE = (
        AppiumBy.XPATH,
        '//*[contains(@resource-id, "batteryPercentage") '
        'or (contains(@text, "%") and not(contains(@text, "kW")))]',
    )

    # Stats row labels
    STAT_LABEL_CURRENT_LOAD = (
        AppiumBy.XPATH,
        '//*[@text="At Current Load" or @content-desc="At Current Load"]',
    )
    STAT_LABEL_STORED_POWER = (
        AppiumBy.XPATH,
        '//*[@text="Stored Power" or @content-desc="Stored Power"]',
    )
    STAT_VALUE_HRS = (
        AppiumBy.XPATH,
        '//*[@text="Hrs" or @content-desc="Hrs"]',
    )
    STAT_VALUE_UNITS = (
        AppiumBy.XPATH,
        '//*[@text="Units" or @content-desc="Units"]',
    )

    # Stats row values (numeric)
    # Current Load: HH:MM format
    CURRENT_LOAD_VALUE = (
        AppiumBy.XPATH,
        '//*[contains(@resource-id, "currentLoad") '
        'or (re:match(@text, "^\\d{2}:\\d{2}$"))]',
    )
    # Stored Power: decimal number
    STORED_POWER_VALUE = (
        AppiumBy.XPATH,
        '//*[contains(@resource-id, "storedPower")]',
    )

    # ── Battery Usage Graph ───────────────────────────────────────────────────
    USAGE_GRAPH_TITLE = (
        AppiumBy.XPATH,
        '//*[@text="Battery Usage Graph" or @content-desc="Battery Usage Graph"]',
    )

    # Y-axis label container for Usage Graph.
    # Each label is a child text view; grab them by index or resource-id prefix.
    USAGE_Y_AXIS_LABEL_CONTAINER = (
        AppiumBy.XPATH,
        '//*[contains(@resource-id, "usageGraph") '
        'or following-sibling::*[@text="Battery Usage Graph"]]',
    )

    # X-axis labels are shared between both graphs (same time buckets).
    # Typical 24-hour buckets shown at 4-hour intervals.
    X_AXIS_VALUES: list[str] = [
        "12 AM", "4 AM", "8 AM", "12 PM", "4 PM", "8 PM",
    ]

    # Expected Y-axis labels – Usage Graph (power in kW, top → bottom)
    # Adjust these values to match what your app actually renders.
    USAGE_Y_AXIS_LABELS_ORDERED: list[str] = [
        "5.0 kW", "4.0 kW", "3.0 kW", "2.0 kW", "1.0 kW", "0.0 kW",
    ]

    # ── Yesterday's Data – Usage Graph ───────────────────────────────────────
    YESTERDAY_LABEL = (
        AppiumBy.XPATH,
        '//*[@text="Yesterday\'s Data" or @content-desc="Yesterday\'s Data"]',
    )
    # The first toggle on the screen (Usage Graph section)
    USAGE_YESTERDAY_TOGGLE = (
        AppiumBy.XPATH,
        '(//*[@class="android.widget.Switch" or contains(@resource-id, "toggle")])[1]',
    )

    # ── Battery SOC Graph ─────────────────────────────────────────────────────
    SOC_GRAPH_TITLE = (
        AppiumBy.XPATH,
        '//*[@text="Battery SOC Graph" or @content-desc="Battery SOC Graph"]',
    )

    # Expected Y-axis labels – SOC Graph (percentages, top → bottom)
    SOC_Y_AXIS_LABELS_ORDERED: list[str] = [
        "100 %", "80 %", "60 %", "40 %", "20 %", "0 %",
    ]

    # ── Yesterday's Data – SOC Graph ─────────────────────────────────────────
    # The second toggle on the screen (SOC Graph section)
    SOC_YESTERDAY_TOGGLE = (
        AppiumBy.XPATH,
        '(//*[@class="android.widget.Switch" or contains(@resource-id, "toggle")])[2]',
    )

    # ── Bottom nav – selected-state detection ─────────────────────────────────
    # React Native bottom tabs typically set selected="true" on the active tab.
    BATTERY_TAB_SELECTED = (
        AppiumBy.XPATH,
        '//*[@selected="true" and '
        '(@content-desc="Battery" or contains(@resource-id, "battery"))]',
    )

    # ══════════════════════════════════════════════════════════════════════════
    # ── Constructor ───────────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def __init__(self, driver) -> None:
        self.driver = driver

    # ══════════════════════════════════════════════════════════════════════════
    # ── Private helpers ───────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def _wait(self, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(
            self.driver,
            timeout,
            poll_frequency=POLL_FREQUENCY,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def _find(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """Return the first element matching *locator*, or raise TimeoutException."""
        return self._wait(timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Element not found: {locator}",
        )

    def _find_all(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> list:
        """
        Return all elements matching *locator*.
        Returns an empty list (not an exception) when nothing is found.
        """
        try:
            self._wait(timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def _is_visible(self, locator: tuple, timeout: int = SHORT_TIMEOUT) -> bool:
        """Return True if the element is present AND displayed within *timeout*."""
        try:
            element = self._wait(timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def _tap(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Wait for an element then tap it."""
        self._wait(timeout).until(
            EC.element_to_be_clickable(locator),
            message=f"Element not clickable: {locator}",
        ).click()

    def _get_text(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> str:
        """Return the text of a located element (stripped)."""
        element = self._find(locator, timeout)
        return (element.text or element.get_attribute("content-desc") or "").strip()

    def _get_toggle_state(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Return the checked / selected state of a Switch / Toggle element.
        Checks both the 'checked' and 'selected' attributes to handle
        React Native rendering quirks.
        """
        element = self._find(locator, timeout)
        checked  = element.get_attribute("checked")
        selected = element.get_attribute("selected")
        return checked == "true" or selected == "true"

    # ══════════════════════════════════════════════════════════════════════════
    # ── Navigation helpers ────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def tap_tab(self, tab_locator: tuple) -> None:
        """Tap any bottom-navigation tab by its locator."""
        self._tap(tab_locator)

    def navigate_to_home(self) -> None:
        """Navigate to the Home tab."""
        self.tap_tab(self.TAB_HOME)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Screen load verification ──────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def is_loaded(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Returns True when the 'Battery Management' title is visible on screen.
        Used to confirm successful screen load or reload.
        """
        return self._is_visible(self.SCREEN_TITLE, timeout=timeout)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Battery status card ───────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def get_battery_percentage(self) -> str:
        """
        Return battery percentage text, e.g. '75%'.

        Strategy 1: look for element whose text matches N% pattern.
        Strategy 2: fall back to resource-id heuristic.
        """
        # Broad search for any text node that looks like "NN%"
        candidates = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[re:match(@text, "^\\d{1,3}%$")]',
        )
        if candidates:
            return candidates[0].text.strip()

        # Fallback: resource-id contains "percentage" or "soc"
        fallback_locator = (
            AppiumBy.XPATH,
            '//*[contains(@resource-id, "percentage") or contains(@resource-id, "soc")]',
        )
        return self._get_text(fallback_locator)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Stats row ─────────────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def get_current_load_value(self) -> str:
        """
        Return the Current Load value in HH:MM format.

        Searches for a text element whose value matches HH:MM pattern.
        """
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[re:match(@text, "^\\d{2}:\\d{2}$")]',
        )
        if elements:
            return elements[0].text.strip()

        # Fallback: resource-id heuristic
        loc = (
            AppiumBy.XPATH,
            '//*[contains(@resource-id, "currentLoad") '
            'or contains(@resource-id, "loadTime") '
            'or contains(@resource-id, "hoursRemaining")]',
        )
        return self._get_text(loc)

    def get_stored_power_value(self) -> str:
        """
        Return the Stored Power value as a numeric string, e.g. '12.5'.

        Looks for a text element near the 'Stored Power' label containing a
        decimal/integer number.
        """
        # Find label, then grab sibling/child with numeric text
        loc = (
            AppiumBy.XPATH,
            '//*[contains(@resource-id, "storedPower") '
            'or contains(@resource-id, "powerValue")]',
        )
        try:
            return self._get_text(loc, timeout=SHORT_TIMEOUT)
        except TimeoutException:
            pass

        # Broad: find any decimal-looking text adjacent to the Stored Power label
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[re:match(@text, "^\\d+(\\.\\d+)?$")]',
        )
        if elements:
            return elements[0].text.strip()

        raise TimeoutException("Could not locate Stored Power value element.")

    # ══════════════════════════════════════════════════════════════════════════
    # ── Battery Usage Graph ───────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def is_usage_graph_visible(self) -> bool:
        """Return True if the Battery Usage Graph title is displayed."""
        return self._is_visible(self.USAGE_GRAPH_TITLE)

    def get_usage_y_axis_labels(self) -> list[str]:
        """
        Return the visible Y-axis labels for the Battery Usage Graph (top → bottom).

        The method attempts two strategies:
        1. Find elements by resource-id pattern specific to the usage graph.
        2. Match text against the known USAGE_Y_AXIS_LABELS_ORDERED list.
        """
        # Strategy 1: resource-id contains "usageYAxis" or "usageY"
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[contains(@resource-id, "usageYAxis") '
            'or contains(@resource-id, "usageY")]',
        )
        if elements:
            return [el.text.strip() for el in elements if el.text.strip()]

        # Strategy 2: match against known label set
        found = []
        for label in self.USAGE_Y_AXIS_LABELS_ORDERED:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@text="{label}" or @content-desc="{label}"]',
            )
            if els:
                found.append(label)

        return found

    def get_usage_x_axis_labels(self) -> list[str]:
        """
        Return the visible X-axis labels for the Battery Usage Graph.

        X-axis labels are time strings (e.g. "12 AM", "4 AM").
        """
        return self._get_x_axis_labels_generic()

    # ══════════════════════════════════════════════════════════════════════════
    # ── Yesterday's Data – Usage Graph ───────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def is_yesterday_label_visible(self) -> bool:
        """Return True if a "Yesterday's Data" label is visible on screen."""
        return self._is_visible(self.YESTERDAY_LABEL)

    def get_usage_yesterday_toggle_state(self) -> bool:
        """Return True if the Usage Graph Yesterday's Data toggle is ON."""
        return self._get_toggle_state(self.USAGE_YESTERDAY_TOGGLE)

    def toggle_usage_yesterday_data(self) -> None:
        """Tap the Usage Graph Yesterday's Data toggle."""
        self._tap(self.USAGE_YESTERDAY_TOGGLE)
        # Brief pause for animation to settle before the next assertion
        time.sleep(0.5)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Scroll to SOC Graph ───────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def scroll_to_soc_graph(self) -> None:
        """
        Scroll down until the Battery SOC Graph title is visible.

        Uses UiAutomator2's UiScrollable to handle any scroll container depth.
        Falls back to a manual swipe loop if the UiScrollable approach fails.
        """
        # Preferred: UiAutomator2 scroll-into-view (works on most scroll containers)
        uia_selector = (
            'new UiScrollable(new UiSelector().scrollable(true))'
            '.scrollIntoView('
            'new UiSelector().textContains("Battery SOC Graph")'
            ')'
        )
        try:
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, uia_selector)
            return
        except (NoSuchElementException, Exception):
            logger.debug("UiScrollable scroll-into-view failed; falling back to swipe loop.")

        # Fallback: swipe upward until the SOC graph title appears
        max_swipes = 8
        for attempt in range(max_swipes):
            if self._is_visible(self.SOC_GRAPH_TITLE, timeout=2):
                return
            self._swipe_up()

        if not self._is_visible(self.SOC_GRAPH_TITLE, timeout=SHORT_TIMEOUT):
            raise TimeoutException(
                "Battery SOC Graph is not visible after scrolling."
            )

    def _swipe_up(self, duration_ms: int = 600) -> None:
        """Swipe upward by ~40 % of the screen height."""
        size   = self.driver.get_window_size()
        width  = size["width"]
        height = self.driver.get_window_size()["height"]
        start_y = int(height * 0.70)
        end_y   = int(height * 0.30)
        mid_x   = width // 2
        self.driver.swipe(mid_x, start_y, mid_x, end_y, duration_ms)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Battery SOC Graph ─────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def is_soc_graph_visible(self) -> bool:
        """Return True if the Battery SOC Graph title is displayed."""
        return self._is_visible(self.SOC_GRAPH_TITLE)

    def get_soc_y_axis_labels(self) -> list[str]:
        """
        Return the visible Y-axis labels for the Battery SOC Graph (top → bottom).

        SOC labels follow the pattern 'NN %' (e.g. '100 %', '80 %', …, '0 %').
        """
        # Strategy 1: resource-id
        elements = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[contains(@resource-id, "socYAxis") '
            'or contains(@resource-id, "socY")]',
        )
        if elements:
            return [el.text.strip() for el in elements if el.text.strip()]

        # Strategy 2: match against the known ordered label set
        found = []
        for label in self.SOC_Y_AXIS_LABELS_ORDERED:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@text="{label}" or @content-desc="{label}"]',
            )
            if els:
                found.append(label)

        return found

    def get_soc_x_axis_labels(self) -> list[str]:
        """Return the visible X-axis labels for the Battery SOC Graph."""
        return self._get_x_axis_labels_generic()

    # ══════════════════════════════════════════════════════════════════════════
    # ── Yesterday's Data – SOC Graph ─────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def get_soc_yesterday_toggle_state(self) -> bool:
        """Return True if the SOC Graph Yesterday's Data toggle is ON."""
        return self._get_toggle_state(self.SOC_YESTERDAY_TOGGLE)

    def toggle_soc_yesterday_data(self) -> None:
        """Tap the SOC Graph Yesterday's Data toggle."""
        self._tap(self.SOC_YESTERDAY_TOGGLE)
        time.sleep(0.5)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Bottom navigation ─────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def is_battery_tab_selected(self) -> bool:
        """
        Return True if the Battery bottom-nav tab has the 'selected' state.

        Checks two attributes React Native commonly uses for tab selection:
        • selected="true"
        • checked="true"
        """
        try:
            element = self._find(self.TAB_BATTERY, timeout=SHORT_TIMEOUT)
            selected = element.get_attribute("selected")
            checked  = element.get_attribute("checked")
            return selected == "true" or checked == "true"
        except TimeoutException:
            # Alternative XPath with explicit selected attribute
            return self._is_visible(self.BATTERY_TAB_SELECTED, timeout=SHORT_TIMEOUT)

    # ══════════════════════════════════════════════════════════════════════════
    # ── Shared / internal helpers ─────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    def _get_x_axis_labels_generic(self) -> list[str]:
        """
        Return all X-axis time labels visible on screen.

        X-axis labels are shared by both graphs. The method collects all
        text nodes matching any value in X_AXIS_VALUES.
        """
        found = []
        for label in self.X_AXIS_VALUES:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@text="{label}" or @content-desc="{label}"]',
            )
            if els:
                found.append(label)
        return found