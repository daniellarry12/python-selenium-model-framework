"""
Change Password Test Suite - Production-Ready Tests

Tests cover:
- Password change validation (mismatch scenario)
- Navigation through account pages using components
- Error message verification with explicit waits

Best Practices Demonstrated:
- Component Object Model (RightMenuComponent)
- Page Object Model with page chaining
- No hard-coded sleeps (uses explicit waits)
- Clear Arrange-Act-Assert pattern
- Descriptive variable names and assertions
- Fast, reliable test execution
"""

import pytest
from pages.login_page import LoginPage
from pages.change_password_page import ChangePasswordPage
from tests.base_test import BaseTest
from utilities.test_data import TestData


@pytest.mark.regression
class TestChangePassword(BaseTest):
    """
    Password change functionality test suite.

    Uses @pytest.mark.regression to categorize non-critical tests:
        pytest -m regression
    """

    def test_password_mismatch_validation(self):
        """
        Test password confirmation mismatch error.

        Verifies:
        - User can navigate to Change Password page via right menu
        - Error appears when password and confirmation don't match
        - Error message is accurate and visible
        - User remains on change password page

        Flow:
        1. Login with valid credentials
        2. Navigate to Password page via right menu component
        3. Enter mismatched passwords
        4. Verify error message appears
        """
        # Arrange
        login_page = LoginPage(self.driver)
        change_password_page = ChangePasswordPage(self.driver)

        new_password = "NewPassword123!"
        mismatched_confirm = "DifferentPassword456!"
        expected_error = "Password confirmation does not match password!"

        # Act - Login
        login_page.set_email_address(TestData.email)
        login_page.set_password(TestData.password)
        my_account_page = login_page.click_login_button()

        # Wait for account page to load (explicit wait - no sleep!)
        my_account_page.wait_for_url_contains("account/account", timeout=10)

        # Act - Navigate to Change Password page using RightMenuComponent
        my_account_page.click_right_menu_page("Password")

        # Wait for password page to load
        change_password_page.wait_for_url_contains("account/password", timeout=10)

        # Act - Attempt password change with mismatch
        change_password_page.change_password(new_password, mismatched_confirm)

        # Assert - Verify error message appears (with explicit wait)
        assert change_password_page.is_confirmation_error_displayed(timeout=5), (
            "Confirmation error message should be displayed when passwords don't match"
        )

        actual_error = change_password_page.get_confirmation_error_message()
        assert actual_error == expected_error, (
            f"Expected error '{expected_error}' but got '{actual_error}'"
        )

        # Verify still on password page (not redirected on error)
        current_url = change_password_page.get_current_url()
        assert "account/password" in current_url, (
            f"Should remain on password page after validation error. "
            f"Current URL: {current_url}"
        )