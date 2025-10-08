import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from config.environment_manager import get_config


def pytest_addoption(parser):
    """Add command line options"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome, firefox, edge, or 'all' for all browsers"
    )
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Environment to test: dev, staging, prod (default: from .env TEST_ENV)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )


@pytest.fixture(scope="session")
def config(request):
    """Get environment configuration"""
    env_name = request.config.getoption("--env")
    return get_config(env_name)


@pytest.fixture(scope="session")
def base_url(config):
    """Get base URL from configuration"""
    return config.BASE_URL


def pytest_generate_tests(metafunc):
    """Dynamically generate tests based on --browser option"""
    if "initialize_driver" in metafunc.fixturenames:
        browser_option = metafunc.config.getoption("--browser").lower()

        if browser_option == "all":
            browsers = ["chrome", "firefox", "edge"]
        else:
            browsers = [browser_option]

        metafunc.parametrize("browser_name", browsers, indirect=False)


@pytest.fixture
def initialize_driver(request, config, base_url, browser_name):
    """Initialize WebDriver with the specified browser and navigate to base URL"""
    browser = browser_name.lower()
    headless = request.config.getoption("--headless")

    # Setup browser with options
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(
            f"Unsupported browser: {browser}. "
            f"Valid options: chrome, firefox, edge"
        )

    # Apply timeouts from config
    driver.implicitly_wait(config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)

    request.cls.driver = driver
    print(f"\nEnvironment: {config.ENVIRONMENT}")
    print(f"Browser: {browser} (headless: {headless})")
    print(f"Base URL: {base_url}")
    driver.get(base_url)
    driver.maximize_window()
    yield
    print("\nClosing driver...")
    driver.quit()




