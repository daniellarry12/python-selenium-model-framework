"""
Browser Factory for creating WebDriver instances.

This module provides a centralized factory for creating production-ready
WebDriver instances with proper options and service configuration.

Design Pattern: Factory Method Pattern
- Centralizes driver creation logic
- Easy to extend (add new browsers)
- Easy to test (isolated methods)
- Hides complexity of driver/service configuration
"""

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
import shutil
from typing import Optional

from drivers.browser_options.chrome_options import ChromeOptionsBuilder
from drivers.browser_options.firefox_options import FirefoxOptionsBuilder
from drivers.browser_options.edge_options import EdgeOptionsBuilder


class BrowserFactory:
    """
    Factory for creating production-ready WebDriver instances.

    This class encapsulates all the complexity of creating WebDriver
    instances for different browsers with proper configuration for
    local, Docker, and CI/CD environments.

    Usage:
        >>> driver = BrowserFactory.create("chrome", headless=True)
        >>> driver.get("https://example.com")
        >>> driver.quit()

        >>> # With custom binary location
        >>> driver = BrowserFactory.create("chrome", headless=False, binary_location="/usr/bin/chromium")
    """

    SUPPORTED_BROWSERS = ["chrome", "firefox", "edge"]

    @staticmethod
    def create(browser: str, headless: bool = False, **kwargs) -> WebDriver:
        """
        Create a WebDriver instance for the specified browser.

        This is the main entry point for creating drivers. It delegates
        to browser-specific creation methods internally.

        Args:
            browser: Browser name ('chrome', 'firefox', 'edge')
            headless: Whether to run in headless mode
            **kwargs: Additional browser-specific options:
                - binary_location (str): Custom browser binary path
                - service_args (list): Additional service arguments

        Returns:
            Configured WebDriver instance

        Raises:
            ValueError: If browser is not supported

        Example:
            >>> driver = BrowserFactory.create('chrome', headless=True)
            >>> driver = BrowserFactory.create('firefox', headless=False)
            >>> driver = BrowserFactory.create('edge', headless=True)
        """
        browser = browser.lower().strip()

        if browser not in BrowserFactory.SUPPORTED_BROWSERS:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                f"Valid options: {', '.join(BrowserFactory.SUPPORTED_BROWSERS)}"
            )

        # Delegate to specific creation method
        if browser == "chrome":
            return BrowserFactory._create_chrome(headless, **kwargs)
        elif browser == "firefox":
            return BrowserFactory._create_firefox(headless, **kwargs)
        elif browser == "edge":
            return BrowserFactory._create_edge(headless, **kwargs)

    @staticmethod
    def _create_chrome(headless: bool, **kwargs) -> WebDriver:
        """
        Create Chrome WebDriver with production-ready options.

        Handles two environments:
        1. Local: Uses Selenium Manager to auto-download ChromeDriver
        2. Docker: Uses system chromedriver with chromium binary

        Args:
            headless: Run in headless mode
            **kwargs: Additional options (binary_location, service_args)

        Returns:
            Configured Chrome WebDriver

        Example:
            >>> driver = BrowserFactory._create_chrome(headless=True)
            >>> driver = BrowserFactory._create_chrome(
            ...     headless=False,
            ...     binary_location="/usr/bin/chromium"
            ... )
        """
        # Build options via builder pattern
        options = ChromeOptionsBuilder.build(headless=headless)

        # Override binary location if provided
        if 'binary_location' in kwargs:
            options.binary_location = kwargs['binary_location']

        # Check for system chromedriver (Docker environment)
        chromium_driver_path = shutil.which("chromedriver")

        if chromium_driver_path:
            # Docker/system environment: use system chromedriver
            service = ChromeService(
                executable_path=chromium_driver_path,
                service_args=kwargs.get('service_args', [])
            )
            return webdriver.Chrome(service=service, options=options)
        else:
            # Local environment: use Selenium Manager (auto-download)
            return webdriver.Chrome(options=options)

    @staticmethod
    def _create_firefox(headless: bool, **kwargs) -> WebDriver:
        """
        Create Firefox WebDriver with production-ready options.

        Firefox uses geckodriver which is auto-detected by Selenium Manager.
        No special Docker handling needed (unlike Chrome).

        Args:
            headless: Run in headless mode
            **kwargs: Additional options (binary_location, service_args)

        Returns:
            Configured Firefox WebDriver

        Example:
            >>> driver = BrowserFactory._create_firefox(headless=True)
            >>> driver = BrowserFactory._create_firefox(
            ...     headless=False,
            ...     binary_location="/usr/bin/firefox"
            ... )
        """
        # Build options via builder pattern
        options = FirefoxOptionsBuilder.build(headless=headless)

        # Override binary location if provided
        if 'binary_location' in kwargs:
            options.binary_location = kwargs['binary_location']

        # Create service if custom service args provided
        if 'service_args' in kwargs:
            service = FirefoxService(service_args=kwargs['service_args'])
            return webdriver.Firefox(service=service, options=options)
        else:
            # Use Selenium Manager (auto-download geckodriver)
            return webdriver.Firefox(options=options)

    @staticmethod
    def _create_edge(headless: bool, **kwargs) -> WebDriver:
        """
        Create Edge WebDriver with production-ready options.

        Edge is Chromium-based, so it's similar to Chrome but uses
        msedgedriver instead of chromedriver.

        Args:
            headless: Run in headless mode
            **kwargs: Additional options (binary_location, service_args)

        Returns:
            Configured Edge WebDriver

        Example:
            >>> driver = BrowserFactory._create_edge(headless=True)
            >>> driver = BrowserFactory._create_edge(
            ...     headless=False,
            ...     binary_location="/usr/bin/microsoft-edge"
            ... )
        """
        # Build options via builder pattern
        options = EdgeOptionsBuilder.build(headless=headless)

        # Override binary location if provided
        if 'binary_location' in kwargs:
            options.binary_location = kwargs['binary_location']

        # Create service if custom service args provided
        if 'service_args' in kwargs:
            service = EdgeService(service_args=kwargs['service_args'])
            return webdriver.Edge(service=service, options=options)
        else:
            # Use Selenium Manager (auto-download msedgedriver)
            return webdriver.Edge(options=options)
