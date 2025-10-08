from pages.base_page import BasePage
from pages.components.right_menu_component import RightMenuComponent


class MyAccountPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.right_menu = RightMenuComponent(driver)

    def click_right_menu_page(self, page_name: str):
        self.right_menu.click_menu_item(page_name)