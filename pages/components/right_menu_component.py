"""
Right Menu Component - Reusable component for sidebar navigation.

This component encapsulates the right-side menu functionality found
on account pages. It demonstrates:

- Component Pattern: Reusable UI components
- Encapsulation: Menu-specific logic isolated
- DRY: Avoid repeating menu logic in multiple pages

Design Pattern: Component Object Model (COM)
- Similar to POM but for UI components that appear across pages
- Can be composed into page objects

Usage:
    from pages.components.right_menu_component import RightMenuComponent
    from pages.base_page import BasePage

    class MyAccountPage(BasePage):
        def __init__(self, driver):
            super().__init__(driver)
            self.right_menu = RightMenuComponent(driver)

        def navigate_to_password(self):
            self.right_menu.click_menu_item("Password")
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage


class RightMenuComponent(BasePage):
    """
    Component for the right sidebar menu on account pages.

    This menu appears on various account pages and provides navigation
    to different account sections (My Account, Password, Address Book, etc.).

    Inherits from BasePage to reuse element interaction methods.
    """

    # Locator strategy: Dynamic XPath to find menu items by text
    # Note: Leading space in text is part of the actual DOM structure
    _MENU_ITEM_XPATH = "//aside[@id='column-right']//a[text()=' {page_name}']"

    def __init__(self, driver: WebDriver):
        """
        Initialize RightMenuComponent.

        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)

    def _get_menu_item_locator(self, page_name: str) -> tuple:
        """
        Build locator for menu item by page name.

        Args:
            page_name: Display name of the menu item (e.g., "Password", "My Account")

        Returns:
            Tuple of (By.XPATH, xpath_string)

        Example:
            locator = self._get_menu_item_locator("Password")
            # Returns: (By.XPATH, "//aside[@id='column-right']//a[text()=' Password']")
        """
        xpath = self._MENU_ITEM_XPATH.format(page_name=page_name)
        return (By.XPATH, xpath)

    def click_menu_item(self, page_name: str) -> None:
        """
        Click a menu item in the right sidebar.

        Args:
            page_name: Display name of the menu item

        Raises:
            TimeoutException: If menu item not found

        Example:
            right_menu.click_menu_item("Password")
            right_menu.click_menu_item("Address Book")
        """
        locator = self._get_menu_item_locator(page_name)
        self.click(*locator)

    def is_menu_item_displayed(self, page_name: str) -> bool:
        """
        Check if a menu item is visible.

        Args:
            page_name: Display name of the menu item

        Returns:
            True if menu item is visible, False otherwise

        Example:
            if right_menu.is_menu_item_displayed("Password"):
                print("User can change password")
        """
        locator = self._get_menu_item_locator(page_name)
        return self.is_displayed(*locator)

    def get_menu_item_text(self, page_name: str) -> str:
        """
        Get the text of a menu item.

        Args:
            page_name: Display name of the menu item

        Returns:
            Menu item text (stripped)

        Example:
            text = right_menu.get_menu_item_text("My Account")
        """
        locator = self._get_menu_item_locator(page_name)
        return self.get_text(*locator)

    def get_all_menu_items(self) -> list:
        """
        Get all visible menu items in the right sidebar.

        Returns:
            List of menu item texts

        Example:
            items = right_menu.get_all_menu_items()
            assert "Password" in items
        """
        menu_items_locator = (By.XPATH, "//aside[@id='column-right']//a")
        elements = self.find_all(*menu_items_locator)
        return [elem.text.strip() for elem in elements if elem.text.strip()]
