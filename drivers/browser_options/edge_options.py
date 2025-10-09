"""
Edge browser options configuration.

This module provides production-ready Edge options that work in:
- Local development environments
- Docker containers (where Edge is available)
- CI/CD environments (GitHub Actions, Jenkins, etc.)

"""

from selenium.webdriver.edge.options import Options as EdgeOptions
import tempfile
import os


class EdgeOptionsBuilder:
    """
    Build production-ready Edge options.

    Note: Since Edge is Chromium-based (since 2020), most options
    are identical to Chrome options.
    """

    @staticmethod
    def build(headless: bool = False) -> EdgeOptions:
    
        options = EdgeOptions()

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
        # Forces Edge to use /tmp instead of /dev/shm for shared memory
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
        # Edge-Specific: InPrivate Mode
        # ====================================================================
        # InPrivate mode ensures clean sessions (no cookies, cache, history)
        # Benefits: Consistent starting state, isolated test runs
        # Note: Disable for performance tests, PWA tests, or session persistence tests
        options.add_argument("--inprivate")

        # ====================================================================
        # Logging Suppression (Cleaner Test Output)
        # ====================================================================
        # Removes verbose Edge logs from console output (especially on Windows)
        # Example output without this: [0108/143022.456:INFO:CONSOLE(1)] "message"
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Disables Edge automation extension
        # Benefits:
        # 1. Removes "Microsoft Edge is being controlled by automated software" banner
        # 2. Faster startup (one less extension to load)
        # 3. Cleaner browser state for testing
        # Note: This replaces deprecated --disable-infobars flag
        options.add_experimental_option('useAutomationExtension', False)

        # ====================================================================
        # Download Settings
        # ====================================================================
        # Create cross-platform temporary download directory
        download_dir = os.path.join(tempfile.gettempdir(), "edge_downloads")
        os.makedirs(download_dir, exist_ok=True)

        prefs = {
            # Cross-platform download directory (works on Windows/Linux/macOS)
            "download.default_directory": download_dir,

            # Auto-download without prompting user (required for headless)
            "download.prompt_for_download": False,

            # Allow Edge to update download directory if needed
            "download.directory_upgrade": True,

            # Enable Microsoft SmartScreen (blocks malware/phishing during tests)
            "safebrowsing.enabled": True
        }

        options.add_experimental_option("prefs", prefs)

        return options