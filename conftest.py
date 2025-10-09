"""
Pytest configuration and fixtures for Selenium test framework.

This module provides ONLY pytest-specific concerns:
- CLI options (--browser, --env, --headless)
- Test parametrization (multiple browsers)
- Fixtures (config, driver initialization)

All driver/browser logic is delegated to drivers/ module.
All environment logic is delegated to config/ module.

Design Patterns:
- Dependency Injection: Config and fixtures via pytest
- Separation of Concerns: Each module has a single responsibility
"""

import pytest
from typing import Generator
from selenium.webdriver.remote.webdriver import WebDriver

from config.environment_manager import get_config, EnvironmentConfig
from drivers.driver_manager import DriverManager


# ============================================================================
# CLI Options
# ============================================================================

def pytest_addoption(parser):
    """
    Add custom command-line options for pytest.

    Usage:
        pytest --browser=chrome --env=staging --headless
        pytest --browser=all  # Run tests on all browsers
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

        browsers = (
            ["chrome", "firefox", "edge"]
            if browser_option == "all"
            else [browser_option]
        )

        metafunc.parametrize("browser_name", browsers, indirect=False)


# ============================================================================
# WebDriver Fixture (Simplified with DriverManager)
# ============================================================================

@pytest.fixture
def initialize_driver(
    request,
    config: EnvironmentConfig,
    base_url: str,
    browser_name: str
) -> Generator[WebDriver, None, None]:
    """
    Initialize WebDriver using DriverManager.

    This fixture:
    1. Creates DriverManager with config
    2. Starts driver (creation + configuration + navigation)
    3. Yields driver to test
    4. Ensures cleanup (even if test fails)

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

    # Create DriverManager (encapsulates all driver logic)
    manager = DriverManager(
        browser=browser_name,
        config=config,
        headless=headless
    )

    # Start driver (creates, configures, navigates)
    driver = manager.start()

    # Attach to test class (for @pytest.mark.usefixtures pattern)
    request.cls.driver = driver

    # Log test context (helpful for CI/CD debugging)
    print(f"\n{'='*70}")
    print(f"🌍 Environment: {config.environment.upper()}")
    print(f"🌐 Browser: {browser_name.upper()} {'(Headless)' if headless else ''}")
    print(f"🔗 Base URL: {base_url}")
    print(f"⏱️  Timeouts: {config.implicit_wait}s implicit | {config.page_load_timeout}s page load")
    print(f"{'='*70}")

    # Yield driver to test (test runs here)
    yield driver

    # Teardown: cleanup via manager
    print(f"\n{'='*70}")
    print(f"🧹 [Teardown] Closing {browser_name} driver...")
    print(f"{'='*70}")
    manager.stop()
