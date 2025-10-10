"""
WebDriver Lifecycle Manager.

This module manages the complete lifecycle of WebDriver instances:
- Creation (via BrowserFactory)
- Configuration (timeouts, window size)
- Navigation (base URL)
- Cleanup (proper quit)

Design Pattern: Facade Pattern
- Provides simple interface to complex subsystems
- Hides details of driver creation + configuration
- Makes pytest fixtures cleaner
"""

from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver

from drivers.browser_factory import BrowserFactory
from config.environment_manager import EnvironmentConfig


class DriverManager:
    """
    Manage WebDriver lifecycle and configuration.

    This class combines:
    - Browser creation (via BrowserFactory)
    - Environment configuration (via EnvironmentConfig)
    - Lifecycle management (start, stop, cleanup)

    It acts as a facade that simplifies the complex interactions between
    browser drivers, configuration, and environment setup.

    Usage:
        >>> from config.environment_manager import get_config
        >>> config = get_config('dev')
        >>> manager = DriverManager('chrome', config, headless=True)
        >>> driver = manager.start()
        >>> # ... run tests ...
        >>> manager.stop()

    Context Manager Support:
        >>> with DriverManager('chrome', config) as driver:
        ...     driver.get('https://example.com')
        ...     # auto-cleanup on exit
    """

    def __init__(
        self,
        browser: str,
        config: EnvironmentConfig,
        headless: bool = False,
        **browser_options
    ):
        """
        Initialize driver manager.

        Args:
            browser: Browser name ('chrome', 'firefox', 'edge')
            config: Environment configuration (from environment_manager)
            headless: Run in headless mode
            **browser_options: Additional browser-specific options
                - prefs (dict): Custom browser preferences
                - binary_location (str): Custom browser binary path

        Example:
            >>> config = get_config('staging')
            >>> manager = DriverManager('chrome', config, headless=True)
            >>> manager = DriverManager(
            ...     'firefox',
            ...     config,
            ...     headless=False,
            ...     prefs={'browser.download.dir': '/tmp'}
            ... )
        """
        self.browser = browser
        self.config = config
        self.headless = headless
        self.browser_options = browser_options
        self._driver: Optional[WebDriver] = None

    def start(self) -> WebDriver:
        """
        Create and configure WebDriver.

        This method performs the following steps in order:
        1. Create driver via BrowserFactory
        2. Apply environment-specific timeouts (from config)
        3. Navigate to base URL (from config)
        4. Maximize window (for consistency)

        Returns:
            Configured WebDriver instance ready for testing

        Raises:
            RuntimeError: If driver already started (must call stop() first)

        Example:
            >>> manager = DriverManager('chrome', config)
            >>> driver = manager.start()
            >>> assert driver.current_url == config.base_url
        """
        if self._driver is not None:
            raise RuntimeError(
                "Driver already started. Call stop() before starting again."
            )

        # ====================================================================
        # Step 1: Create driver via BrowserFactory
        # ====================================================================
        self._driver = BrowserFactory.create(
            browser=self.browser,
            headless=self.headless,
            **self.browser_options
        )

        # ====================================================================
        # Step 2: Apply environment-specific timeouts
        # ====================================================================
        # Implicit wait: time to wait for elements to appear
        self._driver.implicitly_wait(self.config.implicit_wait)

        # Page load timeout: time to wait for page to fully load
        self._driver.set_page_load_timeout(self.config.page_load_timeout)

        # ====================================================================
        # Step 3: Navigate to base URL
        # ====================================================================
        self._driver.get(self.config.base_url)

        # ====================================================================
        # Step 4: Maximize window (for consistency across environments)
        # ====================================================================
        self._driver.maximize_window()

        return self._driver

    def stop(self) -> None:
        """
        Quit driver safely.

        This method handles:
        - Proper driver.quit() to clean up resources
        - Exception handling (cleanup should never fail tests)
        - Safe to call even if driver not started
        - Idempotent (can call multiple times safely)

        Example:
            >>> manager = DriverManager('chrome', config)
            >>> driver = manager.start()
            >>> # ... use driver ...
            >>> manager.stop()  # Safe cleanup
            >>> manager.stop()  # Safe to call again (no-op)
        """
        if self._driver:
            try:
                self._driver.quit()
            except Exception as e:
                # Log but don't raise (cleanup should never fail tests)
                # In production, you might want to log this properly
                print(f"Warning: Error during driver cleanup: {e}")
            finally:
                # Always reset driver to None, even if quit() failed
                self._driver = None

    @property
    def driver(self) -> WebDriver:
        """
        Get current driver instance.

        This property provides access to the underlying WebDriver instance
        after it has been started.

        Returns:
            Active WebDriver instance

        Raises:
            RuntimeError: If driver not started yet

        Example:
            >>> manager = DriverManager('chrome', config)
            >>> manager.start()
            >>> driver = manager.driver  # Get driver instance
            >>> driver.find_element(By.ID, 'search')
        """
        if self._driver is None:
            raise RuntimeError(
                "Driver not started. Call start() first or use context manager."
            )
        return self._driver

    # ========================================================================
    # Context Manager Protocol (enables 'with' statement)
    # ========================================================================

    def __enter__(self) -> WebDriver:
        """
        Enter context: start driver.

        This enables using DriverManager with the 'with' statement for
        automatic cleanup.

        Returns:
            Started WebDriver instance

        Example:
            >>> with DriverManager('chrome', config) as driver:
            ...     driver.get('https://example.com')
            ...     # driver.quit() called automatically on exit
        """
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context: stop driver.

        This is called automatically when exiting a 'with' block,
        ensuring proper cleanup even if an exception occurred.

        Args:
            exc_type: Exception type (if an exception occurred)
            exc_val: Exception value (if an exception occurred)
            exc_tb: Exception traceback (if an exception occurred)

        Returns:
            False: Don't suppress exceptions (let them propagate)

        Example:
            >>> with DriverManager('chrome', config) as driver:
            ...     driver.get('https://example.com')
            ...     raise ValueError("Test error")
            # driver.quit() still called, then ValueError propagates
        """
        self.stop()
        return False  # Don't suppress exceptions
