# import pytest
# from pages.navigation_page import NavigationPage


# @pytest.fixture
# def nav(driver):
#     return NavigationPage(driver)


# def test_tab1_home_selected_by_default(nav):
#     assert nav.get_selected_tab(1) == "true", "Tab 1 (Home) should be selected by default"


# def test_navigate_to_solar_tab(nav):
#     nav.go_to_solar()
#     assert nav.get_selected_tab(2) == "true", "Tab 2 (Solar) should be selected"


# def test_navigate_to_grid_tab(nav):
#     nav.go_to_grid()
#     assert nav.get_selected_tab(3) == "true", "Tab 3 (Grid) should be selected"


# def test_grid_screen_content(nav):
#     nav.go_to_grid()
#     assert nav.get_screen_text("Grid"), "Grid label should be visible on grid screen"


# def test_navigate_to_more_tab(nav):
#     nav.go_to_more()
#     assert nav.get_selected_tab(4) == "true", "Tab 4 (More) should be selected"


# def test_navigate_back_to_home(nav):
#     nav.go_to_more()
#     nav.go_to_home()
#     assert nav.get_selected_tab(1) == "true", "Tab 1 (Home) should be selected after returning"


# def test_home_screen_content(nav):
#     nav.go_to_home()
#     assert nav.get_screen_text("Power"), "Power label should be visible on home screen"


# def test_full_tab_cycle(nav):
#     for tab_num, method in enumerate(
#         [nav.go_to_home, nav.go_to_solar, nav.go_to_grid, nav.go_to_more],
#         start=1
#     ):
#         method()
#         assert nav.get_selected_tab(tab_num) == "true", f"Tab {tab_num} should be selected after clicking"
        


import pytest
from pages.navigation_page import NavigationPage


@pytest.fixture
def nav(driver):
    return NavigationPage(driver)


def test_tab1_home_selected_by_default(nav):
    assert nav.get_selected_tab(1) == "true", "Tab 1 (Home) should be selected by default"


def test_navigate_to_solar_tab(nav):
    nav.go_to_solar()
    assert nav.get_selected_tab(2) == "true", "Tab 2 (Solar) should be selected"

def test_solar_screen_content(nav):
    nav.go_to_solar()
    assert nav.get_screen_text("Solar"), "Solar Production screen should be visible"


def test_navigate_to_grid_tab(nav):
    nav.go_to_grid()
    assert nav.get_selected_tab(3) == "true", "Tab 3 (Grid) should be selected"

def test_grid_screen_content(nav):
    nav.go_to_grid()
    assert nav.get_screen_text("Grid"), "Grid screen should be visible"


def test_navigate_to_battery_tab(nav):
    nav.go_to_battery()
    assert nav.get_selected_tab(4) == "true", "Tab 4 (Battery) should be selected"


def test_battery_screen_content(nav):
    nav.go_to_battery()
    assert nav.get_screen_text("Battery"), "Battery screen should be visible"


def test_navigate_to_more_tab(nav):
    nav.go_to_more()
    assert nav.get_selected_tab(5) == "true", "Tab 5 (More) should be selected"


def test_navigate_back_to_home(nav):
    nav.go_to_more()
    nav.go_to_home()
    assert nav.get_selected_tab(1) == "true", "Tab 1 (Home) should be selected after returning"


def test_home_screen_content(nav):
    nav.go_to_home()
    assert nav.get_screen_text("Power"), "Power label should be visible on home screen"


def test_full_tab_cycle(nav):
    for tab_num, method in enumerate(
        [
            nav.go_to_home,
            nav.go_to_solar,
            nav.go_to_grid,
            nav.go_to_battery,
            nav.go_to_more
        ],
        start=1
    ):
        method()
        assert nav.get_selected_tab(tab_num) == "true", f"Tab {tab_num} should be selected after clicking"