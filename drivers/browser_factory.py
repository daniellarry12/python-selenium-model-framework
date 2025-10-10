from enum import Enum
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Union

from drivers.browser_options.chrome_options import ChromeOptionsBuilder
from drivers.browser_options.firefox_options import FirefoxOptionsBuilder
from drivers.browser_options.edge_options import EdgeOptionsBuilder


"""
    Usage:
        >>> driver = BrowserFactory.create("chrome", headless=True)
        >>> driver = BrowserFactory.create(Browser.CHROME, headless=True)
        >>> driver.get("https://example.com")
        >>> driver.quit()
    """


class Browser(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"

    @classmethod
    def values(cls) -> list:
        return [browser.value for browser in cls]


class BrowserFactory:
    SUPPORTED_BROWSERS = Browser.values()

    @staticmethod
    def create(browser: Union[str, Browser], headless: bool = False) -> WebDriver:
        browser_value = browser.value if isinstance(browser, Browser) else browser
        browser_value = browser_value.lower().strip()

        if browser_value not in BrowserFactory.SUPPORTED_BROWSERS:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                f"Valid options: {', '.join(BrowserFactory.SUPPORTED_BROWSERS)}"
            )

        if browser_value == Browser.CHROME.value:
            return BrowserFactory._create_chrome(headless)
        elif browser_value == Browser.FIREFOX.value:
            return BrowserFactory._create_firefox(headless)
        else:
            return BrowserFactory._create_edge(headless)

    @staticmethod
    def _create_chrome(headless: bool) -> WebDriver:
        options = ChromeOptionsBuilder.build(headless=headless)
        return webdriver.Chrome(options=options)

    @staticmethod
    def _create_firefox(headless: bool) -> WebDriver:
        options = FirefoxOptionsBuilder.build(headless=headless)
        return webdriver.Firefox(options=options)

    @staticmethod
    def _create_edge(headless: bool) -> WebDriver:
        options = EdgeOptionsBuilder.build(headless=headless)
        return webdriver.Edge(options=options)