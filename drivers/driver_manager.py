from selenium.webdriver.remote.webdriver import WebDriver

from drivers.browser_factory import BrowserFactory
from config.environment_manager import EnvironmentConfig


class DriverManager:
    """
    Manage WebDriver lifecycle and configuration.

    Usage:
        >>> config = get_config('dev')
        >>> manager = DriverManager('chrome', config, headless=True)
        >>> driver = manager.driver
        >>> # ... run tests ...
        >>> manager.quit()
    """

    driver: WebDriver

    def __init__(
        self,
        browser: str,
        config: EnvironmentConfig,
        headless: bool = False,
        **browser_options
    ):
        self.driver = BrowserFactory.create(
            browser=browser,
            headless=headless,
            **browser_options
        )

        self.driver.implicitly_wait(config.implicit_wait)
        self.driver.set_page_load_timeout(config.page_load_timeout)
        self.driver.get(config.base_url)
        self.driver.maximize_window()

    def quit(self) -> None:
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Warning: Error during driver cleanup: {e}")
            finally:
                self.driver = None  # type: ignore[assignment]
