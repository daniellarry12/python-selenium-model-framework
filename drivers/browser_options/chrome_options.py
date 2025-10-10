from selenium.webdriver.chrome.options import Options as ChromeOptions
import shutil
import tempfile
import os


class ChromeOptionsBuilder():

    @staticmethod
    def build(headless: bool = False) -> ChromeOptions:
        options = ChromeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1920,1080") # ¿PORQUE AQUI NO USA EL ENUM DONDE SE DETERMINA EL WINDOW SIZE Y COMO SE RELACIONA CON ESTO?
        options.add_argument("--incognito")


        download_dir = os.path.join(tempfile.gettempdir(), "chrome_downloads")
        os.makedirs(download_dir, exist_ok=True)

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }

        options.add_experimental_option("prefs", prefs)

        chromium_binary = shutil.which("chromium")
        if chromium_binary:
            options.binary_location = chromium_binary

        return options
