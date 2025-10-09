"""
Chrome browser options configuration.

This module provides production-ready Chrome options that work in:
- Local development environments
- Docker containers (ARM/x86 architectures)
- CI/CD environments (GitHub Actions, Jenkins, etc.)

"""

from selenium.webdriver.chrome.options import Options as ChromeOptions
import shutil
import tempfile
import os


class ChromeOptionsBuilder:
    

    @staticmethod
    def build(headless: bool = False) -> ChromeOptions:
        """
        Create Chrome options with production-ready settings.

        Args:
            headless: Run in headless mode (no GUI)

        Returns:
            Configured ChromeOptions instance

        Example:
            >>> options = ChromeOptionsBuilder.build(headless=True)
            >>> driver = webdriver.Chrome(options=options)
        """
        options = ChromeOptions()

        # ====================================================================
        # Headless Configuration
        # ====================================================================
        if headless:
            options.add_argument("--headless=new")

        # ====================================================================
        # Stability Options (Critical for Docker/CI/CD)
        # ====================================================================
        # Required for Docker/root environments where sandboxing fails
        options.add_argument("--no-sandbox")

        # Overcomes limited /dev/shm (64MB default) in Docker containers
        # Forces Chrome to use /tmp instead of /dev/shm for shared memory
        options.add_argument("--disable-dev-shm-usage")

        # ====================================================================
        # Performance Optimizations
        # ====================================================================
        # Disables all extensions for faster startup and reduced memory usage
        options.add_argument("--disable-extensions")

        # Blocks browser notification popups that could interfere with tests
        options.add_argument("--disable-notifications")

        # ====================================================================
        # Consistency Options
        # ====================================================================
        # Fixed viewport (Full HD) for consistent screenshots and element positioning
        options.add_argument("--window-size=1920,1080")

        # ====================================================================
        # Chrome-Specific: Incognito Mode
        # ====================================================================
        # Incognito mode ensures clean sessions (no cookies, cache, history)
        # Benefits: Consistent starting state, isolated test runs
        # Note: Disable for performance tests, PWA tests, or session persistence tests
        options.add_argument("--incognito")

        # ====================================================================
        # Logging Suppression (Cleaner Test Output)
        # ====================================================================
        # Removes verbose Chrome logs from console output (especially on Windows)
        # Example output without this: [0108/143022.456:INFO:CONSOLE(1)] "message"
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Disables Chrome automation extension
        # Benefits:
        # 1. Removes "Chrome is being controlled by automated software" banner
        # 2. Faster startup (one less extension to load)
        options.add_experimental_option('useAutomationExtension', False)

        # ====================================================================
        # Download Settings
        # ====================================================================
        # Create cross-platform temporary download directory
        download_dir = os.path.join(tempfile.gettempdir(), "chrome_downloads")
        os.makedirs(download_dir, exist_ok=True)

        prefs = {
            # Cross-platform download directory (works on Windows/Linux/macOS)
            "download.default_directory": download_dir,

            # Auto-download without prompting user (required for headless)
            "download.prompt_for_download": False,

            # Allow Chrome to update download directory if needed
            "download.directory_upgrade": True,

            # Enable Google Safe Browsing (blocks malware/phishing during tests)
            "safebrowsing.enabled": True
        }

        options.add_experimental_option("prefs", prefs)

        # ====================================================================
        # Docker Support: Auto-detect Chromium Binary
        # ====================================================================
        # When running in Docker with chromium-chromedriver package,
        # we need to use the system Chromium binary instead of Chrome
        # shutil.which() searches for executable in system PATH (cross-platform)
        chromium_binary = shutil.which("chromium")
        if chromium_binary:
            options.binary_location = chromium_binary

        return options