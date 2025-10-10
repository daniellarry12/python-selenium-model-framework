from selenium.webdriver.firefox.options import Options as FirefoxOptions
import tempfile
import os


class FirefoxOptionsBuilder:

    @staticmethod
    def build(headless: bool = False) -> FirefoxOptions:
        options = FirefoxOptions()

        if headless:
            options.add_argument("-headless")

        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.add_argument("-private")

        download_dir = os.path.join(tempfile.gettempdir(), "firefox_downloads")
        os.makedirs(download_dir, exist_ok=True)

        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf,application/zip,text/csv,application/octet-stream,"
            "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("geo.enabled", False)

        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", True)
        options.set_preference("browser.sessionstore.resume_from_crash", False)

        return options
