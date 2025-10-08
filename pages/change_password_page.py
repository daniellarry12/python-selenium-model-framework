from pages.base_page import BasePage
from pages.my_account_page import MyAccountPage
from utilities.locator import ChangePasswordLocatorFields


class ChangePasswordPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.locate = ChangePasswordLocatorFields

    def change_password(self, password, confirm_password):
        self.set(self.locate.password_field, password)
        self.set(self.locate.confirm_password_field, confirm_password)
        self.click(self.locate.continue_button)
        return MyAccountPage(self.driver)
    
    def get_confirmation_error_message(self):
        """Get the password confirmation error message text."""
        return self.get_text(self.locate.confirmation_error_message)

    def is_confirmation_error_displayed(self, timeout=5):
        """
        Check if password confirmation error is visible.

        Uses explicit wait from BasePage - waits up to timeout seconds
        for element to appear instead of failing immediately.

        Args:
            timeout: Max seconds to wait for error message

        Returns:
            True if error is visible, False otherwise
        """
        return self.is_displayed(self.locate.confirmation_error_message, timeout=timeout)
       

    