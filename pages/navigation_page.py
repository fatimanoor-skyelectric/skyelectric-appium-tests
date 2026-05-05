# # from appium.webdriver.common.appiumby import AppiumBy

# # class NavigationPage:
    
# #     TAB_1 = (AppiumBy.ACCESSIBILITY_ID, "Tab 1 of 4")  # Home
# #     TAB_2 = (AppiumBy.ACCESSIBILITY_ID, "Tab 2 of 4")  # Solar/Energy
# #     TAB_3 = (AppiumBy.ACCESSIBILITY_ID, "Tab 3 of 4")  # Grid
# #     TAB_4 = (AppiumBy.ACCESSIBILITY_ID, "Tab 4 of 4")  # More

# #     def __init__(self, driver):
# #         self.driver = driver

# #     def go_to_home(self):
# #         self.driver.find_element(*self.TAB_1).click()

# #     def go_to_solar(self):
# #         self.driver.find_element(*self.TAB_2).click()

# #     def go_to_grid(self):
# #         self.driver.find_element(*self.TAB_3).click()

# #     def go_to_more(self):
# #         self.driver.find_element(*self.TAB_4).click()

# #     def get_selected_tab(self, tab_number):
# #         locator = (AppiumBy.ACCESSIBILITY_ID, f"Tab {tab_number} of 4")
# #         element = self.driver.find_element(*locator)
# #         return element.get_attribute("selected")

# #     def get_screen_text(self, content_desc):
# #         try:
# #             el = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, content_desc)
# #             return el.is_displayed()
# #         except:
# #             return False


# #  above is old working code 
# from appium.webdriver.common.appiumby import AppiumBy

# class NavigationPage:

#     # Tabs (NOW 5 TABS)
#     TAB_1 = (AppiumBy.ACCESSIBILITY_ID, "Tab 1 of 5")  # Home
#     TAB_2 = (AppiumBy.ACCESSIBILITY_ID, "Tab 2 of 5")  # Solar/Energy
#     TAB_3 = (AppiumBy.ACCESSIBILITY_ID, "Tab 3 of 5")  # Grid
#     TAB_4 = (AppiumBy.ACCESSIBILITY_ID, "Tab 4 of 5")  # Battery
#     TAB_5 = (AppiumBy.ACCESSIBILITY_ID, "Tab 5 of 5")  # More

#     def __init__(self, driver):
#         self.driver = driver

#     def go_to_home(self):
#         self.driver.find_element(*self.TAB_1).click()

#     def go_to_solar(self):
#         self.driver.find_element(*self.TAB_2).click()

#     def go_to_grid(self):
#         self.driver.find_element(*self.TAB_3).click()

#     def go_to_battery(self):
#         self.driver.find_element(*self.TAB_4).click()

#     def go_to_more(self):
#         self.driver.find_element(*self.TAB_5).click()

#     def get_selected_tab(self, tab_number):
#         locator = (AppiumBy.ACCESSIBILITY_ID, f"Tab {tab_number} of 5")
#         element = self.driver.find_element(*locator)
#         return element.get_attribute("selected")

#     def get_screen_text(self, content_desc):
#         try:
#             el = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, content_desc)
#             return el.is_displayed()
#         except:
#             return False

#  above is working test file 

from appium.webdriver.common.appiumby import AppiumBy

class NavigationPage:

    # Tabs (NOW 5 TABS)
    TAB_1 = (AppiumBy.ACCESSIBILITY_ID, "Tab 1 of 5")  # Home
    TAB_2 = (AppiumBy.ACCESSIBILITY_ID, "Tab 2 of 5")  # Solar/Energy
    TAB_3 = (AppiumBy.ACCESSIBILITY_ID, "Tab 3 of 5")  # Grid
    TAB_4 = (AppiumBy.ACCESSIBILITY_ID, "Tab 4 of 5")  # Battery
    TAB_5 = (AppiumBy.ACCESSIBILITY_ID, "Tab 5 of 5")  # More

    def __init__(self, driver):
        self.driver = driver

    def go_to_home(self):
        self.driver.find_element(*self.TAB_1).click()

    def go_to_solar(self):
        self.driver.find_element(*self.TAB_2).click()

    def go_to_grid(self):
        self.driver.find_element(*self.TAB_3).click()

    def go_to_battery(self):
        self.driver.find_element(*self.TAB_4).click()

    def go_to_more(self):
        self.driver.find_element(*self.TAB_5).click()

    def get_selected_tab(self, tab_number):
        locator = (AppiumBy.ACCESSIBILITY_ID, f"Tab {tab_number} of 5")
        element = self.driver.find_element(*locator)
        return element.get_attribute("selected")

    def get_screen_text(self, content_desc):
        try:
            el = self.driver.find_element(
                AppiumBy.XPATH,
                f"//*[contains(@content-desc, '{content_desc}')]"
            )
            return el.is_displayed()
        except:
            return False