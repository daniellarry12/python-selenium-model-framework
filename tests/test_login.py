"""
Login Test Suite - Production-Ready Tests

Tests cover:
- Valid login flow with explicit waits
- Invalid credentials with proper assertions
- URL verification after navigation
- No hard-coded sleeps (production anti-pattern)

Best Practices Demonstrated:
- Page Object Model usage
- Explicit waits via BasePage methods
- Descriptive assertions with error messages
- Clean test data separation
- Proper fixture usage
- Fast execution (no time.sleep)
"""

import pytest
from pages.login_page import LoginPage
from tests.base_test import BaseTest
from utilities.test_data import TestData


@pytest.mark.smoke
class TestLogin(BaseTest):
    """
    Login functionality test suite.

    Uses @pytest.mark.smoke to allow running critical tests first:
        pytest -m smoke
    """

    def test_valid_credentials(self):
        """
        Test successful login with valid credentials.

        Verifies:
        - User can login with valid email/password
        - Redirected to My Account page
        - Page title matches expected value
        - URL contains 'account/account'
        """
        # Arrange
        login_page = LoginPage(self.driver)
        expected_title = "My Account"
        expected_url_fragment = "account/account"

        # Act
        login_page.set_email_address(TestData.email)
        login_page.set_password(TestData.password)
        my_account_page = login_page.click_login_button()

        # Wait for navigation to complete
        my_account_page.wait_for_url_contains(expected_url_fragment, timeout=10)

        # Assert - Multiple validations for robust verification
        actual_title = my_account_page.get_title()
        assert actual_title == expected_title, (
            f"Expected title '{expected_title}' but got '{actual_title}'"
        )

        actual_url = my_account_page.get_current_url()
        assert expected_url_fragment in actual_url, (
            f"Expected URL to contain '{expected_url_fragment}' but got '{actual_url}'"
        )

    def test_invalid_credentials(self):
        """
        Test login failure with invalid credentials.

        Verifies:
        - Warning message appears for invalid credentials
        - User remains on login page
        - Warning message contains expected text
        - Error message is visible (using explicit wait)
        """
        # Arrange
        login_page = LoginPage(self.driver)
        invalid_email = "invalid_email@notexist.com"
        invalid_password = "WrongPassword123!"
        expected_warning_text = "Warning"

        # Act
        login_page.log_into_application(invalid_email, invalid_password)

        # Assert - Warning message appears (with explicit wait)
        assert login_page.is_warning_message_displayed(timeout=5), (
            "Warning message should be displayed for invalid credentials"
        )

        actual_message = login_page.get_warning_message()
        assert expected_warning_text in actual_message, (
            f"Warning message should contain '{expected_warning_text}' "
            f"but got '{actual_message}'"
        )

        # Verify user is still on login page (not redirected)
        current_url = login_page.get_current_url()
        assert "account/login" in current_url, (
            f"User should remain on login page after invalid credentials. "
            f"Current URL: {current_url}"
        )

    @pytest.mark.parametrize("email,password,expected_error", [
        ("", "", "Warning"),  # Empty credentials
        ("invalidemail", "password", "Warning"),  # Invalid email format
        (TestData.email, "wrongpassword", "Warning"),  # Valid email, wrong password
    ])
    def test_login_validation_scenarios(self, email, password, expected_error):
        """
        Test multiple login validation scenarios using parametrization.

        This demonstrates CI/CD optimization:
        - Single test method tests multiple scenarios
        - Reduces code duplication
        - Runs in parallel when using pytest-xdist

        Args:
            email: Email to test
            password: Password to test
            expected_error: Expected error text in warning message
        """
        # Arrange
        login_page = LoginPage(self.driver)

        # Act
        login_page.log_into_application(email, password)

        # Assert
        assert login_page.is_warning_message_displayed(timeout=5), (
            f"Warning should appear for email='{email}' password='{password}'"
        )

        actual_message = login_page.get_warning_message()
        assert expected_error in actual_message, (
            f"Expected '{expected_error}' in warning message, got '{actual_message}'"
        )
