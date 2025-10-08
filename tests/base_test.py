import pytest
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.mark.usefixtures("initialize_driver")
class BaseTest:
    driver: WebDriver
    