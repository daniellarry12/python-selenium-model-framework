from selenium.webdriver.edge.options import Options as EdgeOptions
import tempfile
import os


class EdgeOptionsBuilder:

    @staticmethod
    def build(headless: bool = False) -> EdgeOptions:
        options = EdgeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--inprivate")


        download_dir = os.path.join(tempfile.gettempdir(), "edge_downloads")
        os.makedirs(download_dir, exist_ok=True)

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }

        options.add_experimental_option("prefs", prefs)

        return options
