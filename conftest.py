"""
Pytest configuration and fixtures for Selenium test framework.

This module provides:
- CLI options for browser, environment, and headless mode
- Session-scoped configuration fixture
- Browser Factory for creating production-ready WebDriver instances
- Common test fixtures with proper teardown

Design Patterns:
- Factory Pattern: BrowserFactory for driver creation
- Dependency Injection: Config and fixtures via pytest
- Single Responsibility: Each component does one thing well
"""

import pytest
from typing import Generator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from config.environment_manager import get_config, EnvironmentConfig


# ============================================================================
# CLI Options
# ============================================================================

def pytest_addoption(parser):
    """
    Add custom command-line options for pytest.

    Usage:
        pytest --browser=chrome --env=staging --headless
    """
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser: chrome, firefox, edge, or 'all' for all browsers"
    )
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Environment: dev, staging, prod (default: TEST_ENV from .env)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def config(request) -> EnvironmentConfig:
    """
    Load environment configuration once per test session.

    Returns:
        EnvironmentConfig: Immutable config with all settings

    Example:
        def test_timeouts(config):
            assert config.implicit_wait == 10
    """
    env_name = request.config.getoption("--env")
    return get_config(env_name)


@pytest.fixture(scope="session")
def base_url(config: EnvironmentConfig) -> str:
    """
    Get base URL from configuration.

    Example:
        def test_homepage(driver, base_url):
            driver.get(base_url)
            assert "Welcome" in driver.title
    """
    return config.base_url


# ============================================================================
# Browser Parametrization
# ============================================================================

def pytest_generate_tests(metafunc):
    """
    Dynamically parametrize tests for multiple browsers.

    This hook generates test variants when --browser=all is used.

    Example:
        pytest --browser=all
        # Runs: test_login[chrome], test_login[firefox], test_login[edge]
    """
    if "initialize_driver" in metafunc.fixturenames:
        browser_option = metafunc.config.getoption("--browser").lower()

        if browser_option == "all":
            browsers = ["chrome", "firefox", "edge"]
        else:
            browsers = [browser_option]

        metafunc.parametrize("browser_name", browsers, indirect=False)


# ============================================================================
# Browser Factory (Production-Ready)
# ============================================================================

class BrowserFactory:
    """
    Factory for creating production-ready WebDriver instances.

    This class encapsulates browser-specific configurations optimized for:
    - Stability (no random crashes)
    - CI/CD environments (Docker, GitHub Actions)
    - Performance (fast page loads)
    - Consistency (same behavior local and CI)

    Design Pattern: Factory Method Pattern
    - Centralizes driver creation logic
    - Easy to extend (add new browsers)
    - Easy to test (isolated methods)
    """

    @staticmethod
    def create_driver(browser: str, headless: bool = False) -> WebDriver:
        """
        Create a production-ready WebDriver instance.

        Args:
            browser: Browser name ('chrome', 'firefox', 'edge')
            headless: Whether to run in headless mode

        Returns:
            Configured WebDriver instance

        Raises:
            ValueError: If browser is not supported

        Example:
            driver = BrowserFactory.create_driver('chrome', headless=True)
            driver.get('https://example.com')
            driver.quit()
        """
        browser = browser.lower().strip()

        if browser == "chrome":
            return BrowserFactory._create_chrome(headless)
        elif browser == "firefox":
            return BrowserFactory._create_firefox(headless)
        elif browser == "edge":
            return BrowserFactory._create_edge(headless)
        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                f"Valid options: chrome, firefox, edge"
            )

    @staticmethod
    def _create_chrome(headless: bool) -> WebDriver:
        """
        Create Chrome WebDriver with production-ready options.

        Chrome-specific optimizations:
        - Headless mode using new implementation (faster, more stable)
        - No sandbox mode for Docker/CI environments
        - Disable dev-shm to prevent crashes in limited memory
        - Consistent window size for screenshot consistency
        - Suppress unnecessary logging

        Args:
            headless: Run in headless mode

        Returns:
            Configured Chrome WebDriver
        """
        options = ChromeOptions()

        # Headless configuration (if enabled)
        if headless:
            options.add_argument("--headless=new")  # New headless mode (Chrome 109+)
            options.add_argument("--disable-gpu")    # Disable GPU in headless

        # Stability options (critical for CI/CD)
        options.add_argument("--no-sandbox")  # Required for Docker/root environments
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited /dev/shm in Docker
        options.add_argument("--disable-setuid-sandbox")  # Alternative sandbox for CI

        # Performance optimizations
        options.add_argument("--disable-extensions")  # Faster startup
        options.add_argument("--disable-infobars")    # Remove "Chrome is being controlled" banner
        options.add_argument("--disable-notifications")  # Block notification popups

        # Consistency options
        options.add_argument("--window-size=1920,1080")  # Fixed viewport for consistent screenshots
        options.add_argument("--start-maximized")        # Maximize window

        # Logging suppression (cleaner test output)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)

        # User agent (prevents bot detection)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Download settings (if needed)
        prefs = {
            "download.default_directory": "/tmp/downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        # Check if running in Docker with chromium-driver installed
        import shutil
        from selenium.webdriver.chrome.service import Service

        chromium_driver = shutil.which("chromedriver")
        if chromium_driver:
            # Use system chromedriver (Docker environment)
            service = Service(executable_path=chromium_driver)
            # Set binary location for Chromium
            chromium_binary = shutil.which("chromium")
            if chromium_binary:
                options.binary_location = chromium_binary
            return webdriver.Chrome(service=service, options=options)
        else:
            # Use Selenium Manager (local environment)
            return webdriver.Chrome(options=options)

    @staticmethod
    def _create_firefox(headless: bool) -> WebDriver:
        """
        Create Firefox WebDriver with production-ready options.

        Firefox-specific optimizations:
        - Headless mode using native flag
        - Custom preferences for downloads and popups
        - Disable notifications and geolocation prompts
        - Logging configuration

        Args:
            headless: Run in headless mode

        Returns:
            Configured Firefox WebDriver
        """
        options = FirefoxOptions()

        # Headless configuration (if enabled)
        if headless:
            options.add_argument("--headless")

        # Window size (consistency)
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        # Preferences (Firefox uses set_preference instead of arguments)
        # Download preferences
        options.set_preference("browser.download.folderList", 2)  # 0=Desktop, 1=Downloads, 2=Custom
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", "/tmp/downloads")
        options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                              "application/pdf,application/zip,text/csv")

        # Disable notifications and popups
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("geo.enabled", False)  # Disable geolocation prompts

        # Performance optimizations
        options.set_preference("browser.cache.disk.enable", False)  # Disable disk cache
        options.set_preference("browser.cache.memory.enable", True)  # Use memory cache
        options.set_preference("browser.sessionstore.resume_from_crash", False)

        # Security (allow mixed content if needed for testing)
        options.set_preference("security.mixed_content.block_active_content", False)

        # Logging
        options.set_preference("devtools.console.stdout.content", True)

        return webdriver.Firefox(options=options)

    @staticmethod
    def _create_edge(headless: bool) -> WebDriver:
        """
        Create Edge WebDriver with production-ready options.

        Edge-specific optimizations:
        - Similar to Chrome (both are Chromium-based)
        - Additional Edge-specific flags
        - InPrivate mode for clean sessions

        Args:
            headless: Run in headless mode

        Returns:
            Configured Edge WebDriver
        """
        options = EdgeOptions()

        # Headless configuration (if enabled)
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # Stability options (same as Chrome - Chromium-based)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-setuid-sandbox")

        # Performance optimizations
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")

        # Consistency options
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        # Edge-specific: InPrivate mode (clean sessions)
        options.add_argument("--inprivate")

        # Logging suppression
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # User agent
        options.add_argument("--disable-blink-features=AutomationControlled")

        return webdriver.Edge(options=options)


# ============================================================================
# WebDriver Fixture
# ============================================================================

@pytest.fixture
def initialize_driver(
    request,
    config: EnvironmentConfig,
    base_url: str,
    browser_name: str
) -> Generator[WebDriver, None, None]:
    """
    Initialize WebDriver using BrowserFactory and provide to test.

    This fixture:
    1. Creates driver via BrowserFactory (production-ready config)
    2. Applies environment-specific timeouts
    3. Navigates to base URL
    4. Yields driver to test
    5. Ensures cleanup (quit) even if test fails

    Args:
        request: Pytest request object
        config: Environment configuration
        base_url: Application base URL
        browser_name: Browser name (from parametrization)

    Yields:
        WebDriver: Production-ready driver instance

    Example:
        @pytest.mark.usefixtures("initialize_driver")
        class TestLogin:
            def test_login(self):
                self.driver.find_element(By.ID, "username").send_keys("admin")
    """
    headless = request.config.getoption("--headless")

    # Create driver using factory pattern (all production configs applied)
    driver = BrowserFactory.create_driver(browser_name, headless)

    # Apply environment-specific timeouts from config
    driver.implicitly_wait(config.implicit_wait)
    driver.set_page_load_timeout(config.page_load_timeout)

    # Attach driver to test class (for @pytest.mark.usefixtures pattern)
    request.cls.driver = driver

    # Log test context (helpful for CI/CD debugging)
    print(f"\n{'='*70}")
    print(f"🌍 Environment: {config.environment.upper()}")
    print(f"🌐 Browser: {browser_name.upper()} {'(Headless)' if headless else ''}")
    print(f"🔗 Base URL: {base_url}")
    print(f"⏱️  Implicit Wait: {config.implicit_wait}s | Page Load: {config.page_load_timeout}s")
    print(f"{'='*70}")

    # Navigate to base URL
    driver.get(base_url)
    driver.maximize_window()

    # Yield driver to test (test runs here)
    yield driver

    # Teardown: ensure driver quits even if test fails
    print(f"\n{'='*70}")
    print(f"🧹 [Teardown] Closing {browser_name} driver...")
    print(f"{'='*70}")
    driver.quit()