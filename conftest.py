import pytest
from typing import Iterator
from selenium.webdriver.remote.webdriver import WebDriver

from config.environment_manager import get_config, EnvironmentConfig
from drivers.driver_manager import DriverManager

SEPARATOR = "=" * 70


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default="chrome",
        help="Browser: chrome, firefox, edge, or 'all' for all browsers"
    )
    parser.addoption(
        "--env",
        default=None,
        help="Environment: dev, staging, prod (default: TEST_ENV from .env)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )


@pytest.fixture(scope="session")
def config(request) -> EnvironmentConfig:
    env_name = request.config.getoption("--env")
    return get_config(env_name)


def pytest_generate_tests(metafunc):
    if "initialize_driver" in metafunc.fixturenames:
        browser_option = metafunc.config.getoption("--browser").lower()
        browsers = ["chrome", "firefox", "edge"] if browser_option == "all" else [browser_option]
        metafunc.parametrize("browser_name", browsers)


@pytest.fixture
def initialize_driver(
    request,
    config: EnvironmentConfig,
    browser_name: str
) -> Iterator[WebDriver]:
    headless = request.config.getoption("--headless")

    manager = DriverManager(browser_name, config, headless)

    assert manager.driver is not None, "Driver should be initialized"

    request.cls.driver = manager.driver

    print(f"\n{SEPARATOR}")
    print(f"Environment: {config.environment.upper()}")
    print(f"Browser: {browser_name.upper()} {'(Headless)' if headless else ''}")
    print(f"Base URL: {config.base_url}")
    print(f"Timeouts: {config.implicit_wait}s implicit | {config.page_load_timeout}s page load")
    print(SEPARATOR)

    yield manager.driver

    print(f"\n{SEPARATOR}")
    print(f"[Teardown] Closing {browser_name} driver...")
    print(SEPARATOR)
    manager.quit()
