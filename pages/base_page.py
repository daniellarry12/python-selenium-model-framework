"""
Base Page Object - World-Class Foundation

Enterprise-grade base page with commonly used methods organized by category.
Optimized for stability, readability, and ease of use.

Design Patterns:
- Page Object Model (POM)
- Explicit Waits (production-ready)
- DRY Principle
"""

from typing import List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoAlertPresentException


class BasePage:
    """
    Base class for all Page Objects.

    Contains essential methods used across all pages, organized by category:
    - Element Finding & Waiting
    - Element Interaction
    - Information Retrieval
    - Navigation
    - Advanced Actions
    - Alerts & Windows
    """

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initialize BasePage.

        Args:
            driver: WebDriver instance
            timeout: Default wait timeout in seconds
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    # ========================================================================
    # CATEGORY 1: Element Finding & Waiting
    # ========================================================================

    def find(self, *locator) -> WebElement:
        """
        Find element with explicit wait.

        Args:
            locator: (By.STRATEGY, "value") or By.STRATEGY, "value"

        Returns:
            WebElement

        Example:
            element = self.find(*self.email_field)
            element = self.find(self.email_field)
        """
        # Handle both calling styles: find(By.ID, "x") and find((By.ID, "x"))
        if len(locator) == 1 and isinstance(locator[0], tuple):
            locator = locator[0]

        try:
            return self.wait.until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element {locator} not found after {self.timeout}s. "
                f"URL: {self.driver.current_url}"
            )

    def find_all(self, *locator) -> List[WebElement]:
        """
        Find all matching elements.

        Args:
            locator: (By.STRATEGY, "value") or By.STRATEGY, "value"

        Returns:
            List of WebElements (empty if none found)

        Example:
            items = self.find_all(*self.product_items)
            items = self.find_all(self.product_items)
        """
        # Handle both calling styles
        if len(locator) == 1 and isinstance(locator[0], tuple):
            locator = locator[0]

        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def wait_until_visible(self, *locator, timeout: int = None) -> WebElement:
        """
        Wait for element to be visible.

        Args:
            locator: (By.STRATEGY, "value") or By.STRATEGY, "value"
            timeout: Custom timeout (optional)

        Returns:
            Visible WebElement

        Example:
            modal = self.wait_until_visible(*self.success_modal)
            modal = self.wait_until_visible(self.success_modal)
        """
        # Handle both calling styles
        if len(locator) == 1 and isinstance(locator[0], tuple):
            locator = locator[0]

        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def wait_until_invisible(self, *locator, timeout: int = None) -> bool:
        """
        Wait for element to become invisible.

        Useful for loading spinners, overlays, etc.

        Args:
            locator: (By.STRATEGY, "value") or By.STRATEGY, "value"
            timeout: Custom timeout (optional)

        Returns:
            True when invisible

        Example:
            self.wait_until_invisible(*self.loading_spinner)
            self.wait_until_invisible(self.loading_spinner)
        """
        # Handle both calling styles
        if len(locator) == 1 and isinstance(locator[0], tuple):
            locator = locator[0]

        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.invisibility_of_element_located(locator))

    def wait_until_clickable(self, *locator, timeout: int = None) -> WebElement:
        """
        Wait for element to be clickable.

        Args:
            locator: (By.STRATEGY, "value") or By.STRATEGY, "value"
            timeout: Custom timeout (optional)

        Returns:
            Clickable WebElement

        Example:
            button = self.wait_until_clickable(*self.submit_btn)
            button = self.wait_until_clickable(self.submit_btn)
        """
        # Handle both calling styles
        if len(locator) == 1 and isinstance(locator[0], tuple):
            locator = locator[0]

        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    # ========================================================================
    # CATEGORY 2: Element Interaction
    # ========================================================================

    def click(self, *locator) -> None:
        """
        Click element (waits for clickability).

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.click(*self.login_button)
        """
        element = self.wait_until_clickable(*locator)
        try:
            element.click()
        except Exception:
            # Fallback: JavaScript click
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator, value: str) -> None:
        """
        Type text into input field (appends to existing text).

        Args:
            locator: (By.STRATEGY, "value")
            value: Text to type

        Example:
            self.type(self.search_field, "automation")
        """
        element = self.find(*locator)
        element.send_keys(value)

    def clear_and_type(self, locator, value: str) -> None:
        """
        Clear field and type text (most common use case).

        Args:
            locator: (By.STRATEGY, "value")
            value: Text to enter

        Example:
            self.clear_and_type(self.email_field, "user@test.com")
        """
        element = self.find(*locator)
        element.clear()
        element.send_keys(value)

    def set(self, locator, value: str) -> None:
        """
        Alias for clear_and_type (backward compatibility).

        Args:
            locator: (By.STRATEGY, "value")
            value: Text to enter
        """
        self.clear_and_type(locator, value)

    def select_dropdown_by_text(self, locator, text: str) -> None:
        """
        Select dropdown option by visible text.

        Args:
            locator: (By.STRATEGY, "value")
            text: Visible text of option

        Example:
            self.select_dropdown_by_text(self.country_dropdown, "Mexico")
        """
        element = self.find(*locator)
        Select(element).select_by_visible_text(text)

    def select_dropdown_by_value(self, locator, value: str) -> None:
        """
        Select dropdown option by value attribute.

        Args:
            locator: (By.STRATEGY, "value")
            value: Value attribute of option

        Example:
            self.select_dropdown_by_value(self.country_dropdown, "mx")
        """
        element = self.find(*locator)
        Select(element).select_by_value(value)

    def check_checkbox(self, *locator) -> None:
        """
        Check checkbox (if not already checked).

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.check_checkbox(*self.terms_checkbox)
        """
        element = self.find(*locator)
        if not element.is_selected():
            element.click()

    def uncheck_checkbox(self, *locator) -> None:
        """
        Uncheck checkbox (if checked).

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.uncheck_checkbox(*self.newsletter_checkbox)
        """
        element = self.find(*locator)
        if element.is_selected():
            element.click()

    # ========================================================================
    # CATEGORY 3: Information Retrieval
    # ========================================================================

    def get_text(self, *locator) -> str:
        """
        Get visible text from element.

        Args:
            locator: (By.STRATEGY, "value")

        Returns:
            Element text (stripped)

        Example:
            message = self.get_text(*self.error_message)
        """
        element = self.find(*locator)
        return element.text.strip()

    def get_attribute(self, locator, attribute: str) -> str:
        """
        Get attribute value from element.

        Args:
            locator: (By.STRATEGY, "value")
            attribute: Attribute name (e.g., "href", "class", "value")

        Returns:
            Attribute value

        Example:
            url = self.get_attribute(self.link, "href")
        """
        element = self.find(*locator)
        return element.get_attribute(attribute)

    def get_value(self, *locator) -> str:
        """
        Get value attribute (shortcut for input fields).

        Args:
            locator: (By.STRATEGY, "value")

        Returns:
            Value attribute

        Example:
            current_email = self.get_value(*self.email_field)
        """
        return self.get_attribute(locator, "value")

    def is_displayed(self, *locator, timeout: int = 5) -> bool:
        """
        Check if element is visible (non-blocking).

        Args:
            locator: (By.STRATEGY, "value")
            timeout: Wait timeout (default: 5s)

        Returns:
            True if visible, False otherwise

        Example:
            if self.is_displayed(*self.error_message):
                print("Error occurred")
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            return element.is_displayed()
        except TimeoutException:
            return False

    def is_enabled(self, *locator) -> bool:
        """
        Check if element is enabled.

        Returns:
            True if enabled, False if disabled

        Example:
            if self.is_enabled(*self.submit_btn):
                self.click(*self.submit_btn)
        """
        element = self.find(*locator)
        return element.is_enabled()

    def is_selected(self, *locator) -> bool:
        """
        Check if checkbox/radio is selected.

        Returns:
            True if selected

        Example:
            if self.is_selected(*self.remember_me_checkbox):
                print("Remember me is checked")
        """
        element = self.find(*locator)
        return element.is_selected()

    def get_element_count(self, *locator) -> int:
        """
        Get count of matching elements.

        Returns:
            Number of elements found

        Example:
            product_count = self.get_element_count(*self.product_items)
        """
        return len(self.find_all(*locator))

    # ========================================================================
    # CATEGORY 4: Navigation
    # ========================================================================

    def go_to(self, url: str) -> None:
        """
        Navigate to URL.

        Args:
            url: Full URL

        Example:
            self.go_to("https://example.com/login")
        """
        self.driver.get(url)

    def refresh(self) -> None:
        """Refresh current page."""
        self.driver.refresh()

    def get_current_url(self) -> str:
        """
        Get current page URL.

        Returns:
            Current URL

        Example:
            assert "/dashboard" in self.get_current_url()
        """
        return self.driver.current_url

    def get_title(self) -> str:
        """
        Get page title.

        Returns:
            Page title

        Example:
            assert "Login" in self.get_title()
        """
        return self.driver.title

    def wait_for_url_contains(self, url_fragment: str, timeout: int = None) -> bool:
        """
        Wait for URL to contain specific text.

        Useful after navigation/redirects.

        Args:
            url_fragment: Text that should be in URL
            timeout: Custom timeout

        Returns:
            True when URL contains fragment

        Example:
            self.wait_for_url_contains("/dashboard")
        """
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.url_contains(url_fragment))

    def wait_for_title_contains(self, title_fragment: str, timeout: int = None) -> bool:
        """
        Wait for title to contain specific text.

        Args:
            title_fragment: Text that should be in title
            timeout: Custom timeout

        Returns:
            True when title contains fragment

        Example:
            self.wait_for_title_contains("Dashboard")
        """
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.title_contains(title_fragment))

    # ========================================================================
    # CATEGORY 5: Advanced Actions
    # ========================================================================

    def scroll_to_element(self, *locator) -> None:
        """
        Scroll element into view.

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.scroll_to_element(*self.footer_link)
        """
        element = self.find(*locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self) -> None:
        """Scroll to top of page."""
        self.driver.execute_script("window.scrollTo(0, 0);")

    def hover(self, *locator) -> None:
        """
        Hover over element.

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.hover(*self.menu_item)
        """
        element = self.find(*locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def double_click(self, *locator) -> None:
        """
        Double-click element.

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.double_click(*self.folder_icon)
        """
        element = self.find(*locator)
        ActionChains(self.driver).double_click(element).perform()

    def right_click(self, *locator) -> None:
        """
        Right-click element (context menu).

        Args:
            locator: (By.STRATEGY, "value")

        Example:
            self.right_click(*self.file_item)
        """
        element = self.find(*locator)
        ActionChains(self.driver).context_click(element).perform()

    def drag_and_drop(self, source_locator, target_locator) -> None:
        """
        Drag element from source to target.

        Args:
            source_locator: Source element locator
            target_locator: Target element locator

        Example:
            self.drag_and_drop(self.task, self.done_column)
        """
        source = self.find(*source_locator)
        target = self.find(*target_locator)
        ActionChains(self.driver).drag_and_drop(source, target).perform()

    # ========================================================================
    # CATEGORY 6: Alerts & Windows
    # ========================================================================

    def accept_alert(self) -> None:
        """
        Accept/click OK on alert.

        Example:
            self.accept_alert()
        """
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            pass

    def dismiss_alert(self) -> None:
        """
        Dismiss/click Cancel on alert.

        Example:
            self.dismiss_alert()
        """
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except NoAlertPresentException:
            pass

    def get_alert_text(self) -> str:
        """
        Get text from alert.

        Returns:
            Alert text

        Example:
            message = self.get_alert_text()
        """
        alert = self.driver.switch_to.alert
        return alert.text

    def switch_to_window(self, window_index: int = -1) -> None:
        """
        Switch to window by index.

        Args:
            window_index: Window index (default: -1 for last window)

        Example:
            self.switch_to_window(-1)  # Switch to newest window
        """
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[window_index])

    def close_current_window(self) -> None:
        """Close current window/tab."""
        self.driver.close()

    def switch_to_frame(self, *locator) -> None:
        """
        Switch to iframe.

        Args:
            locator: Frame locator

        Example:
            self.switch_to_frame(*self.payment_iframe)
        """
        frame = self.find(*locator)
        self.driver.switch_to.frame(frame)

    def switch_to_default_content(self) -> None:
        """Switch back to main content (exit iframe)."""
        self.driver.switch_to.default_content()