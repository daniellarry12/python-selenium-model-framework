import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def pytest_addoption(parser):
    """Add command line option to select browsers"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome, firefox, edge, or 'all' for all browsers"
    )


@pytest.fixture(scope="session")
def base_url():
    """Get base URL from environment variables"""
    url = os.getenv("BASE_URL")
    if not url:
        raise ValueError(
            "BASE_URL environment variable is not set. "
            "Please create a .env file or set the BASE_URL environment variable. "
            "See .env.example for reference."
        )
    return url


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
def initialize_driver(request, base_url, browser_name):
    """Initialize WebDriver with the specified browser and navigate to base URL"""
    browser = browser_name.lower()

    if browser == "chrome":
        driver = webdriver.Chrome()
    elif browser == "firefox":
        driver = webdriver.Firefox()
    elif browser == "edge":
        driver = webdriver.Edge()
    else:
        raise ValueError(
            f"Unsupported browser: {browser}. "
            f"Valid options: chrome, firefox, edge"
        )

    request.cls.driver = driver
    print(f"\nBrowser: {browser}")
    print(f"Base URL: {base_url}")
    driver.get(base_url)
    driver.maximize_window()
    yield
    print("\nClosing driver...")
    driver.quit()




