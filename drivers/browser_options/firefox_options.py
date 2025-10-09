"""
Firefox browser options configuration.

This module provides production-ready Firefox options that work in:
- Local development environments
- Docker containers
- CI/CD environments (GitHub Actions, Jenkins, etc.)

Note: Firefox uses Gecko engine (not Chromium), so options differ from Chrome/Edge.

Design Pattern: Builder Pattern
- Separation of concerns (options isolated from driver creation)
- Testable (can unit test options without starting browser)
- Reusable (can be used outside pytest)
"""

from selenium.webdriver.firefox.options import Options as FirefoxOptions
import tempfile
import os


class FirefoxOptionsBuilder:
    """
    Build production-ready Firefox options.

    This class provides static methods to create FirefoxOptions with
    all necessary configurations for stability, performance, and
    compatibility across different environments.

    Note: Firefox uses set_preference() for configuration instead of
    add_argument() like Chromium browsers.
    """

    @staticmethod
    def build(headless: bool = False) -> FirefoxOptions:
        """
        Create Firefox options with production-ready settings.

        Args:
            headless: Run in headless mode (no GUI)

        Returns:
            Configured FirefoxOptions instance

        Example:
            >>> options = FirefoxOptionsBuilder.build(headless=True)
            >>> driver = webdriver.Firefox(options=options)
        """
        options = FirefoxOptions()

        # ====================================================================
        # Headless Configuration
        # ====================================================================
        if headless:
            # Modern approach (Selenium 4.10+)
            # Note: Deprecated method (options.headless = True) was removed in Selenium 4.10
            # Use add_argument() for full control and compatibility
            options.add_argument("-headless")

        # ====================================================================
        # Window Size (Consistency)
        # ====================================================================
        # Firefox uses different argument syntax than Chromium browsers
        # Note: These are arguments, not preferences
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        # ====================================================================
        # Firefox-Specific: Private Browsing Mode
        # ====================================================================
        # Private mode ensures clean sessions (no cookies, cache, history)
        # Benefits: Consistent starting state, isolated test runs
        # Note: Disable for performance tests, PWA tests, or session persistence tests
        options.add_argument("-private")

        # ====================================================================
        # Download Preferences
        # ====================================================================
        # Create cross-platform temporary download directory
        download_dir = os.path.join(tempfile.gettempdir(), "firefox_downloads")
        os.makedirs(download_dir, exist_ok=True)

        # Firefox download behavior:
        # browser.download.folderList:
        #   0 = Desktop
        #   1 = System default Downloads folder
        #   2 = Custom location (specified in browser.download.dir)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", download_dir)

        # Don't show download manager window
        options.set_preference("browser.download.manager.showWhenStarting", False)

        # Auto-download common MIME types without prompting
        # Add more MIME types as needed for your tests
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf,application/zip,text/csv,application/octet-stream,"
            "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # ====================================================================
        # Disable Notifications and Prompts
        # ====================================================================
        # Web notifications (push notifications from websites)
        options.set_preference("dom.webnotifications.enabled", False)

        # Push API (server-sent notifications)
        options.set_preference("dom.push.enabled", False)

        # Geolocation prompts ("Allow site to access your location?")
        options.set_preference("geo.enabled", False)

        # ====================================================================
        # Performance Optimizations
        # ====================================================================
        # Disable disk cache (use memory only)
        # Benefits: Faster, no disk I/O, clean state between runs
        # Trade-off: Uses more RAM (acceptable in testing)
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", True)

        # Don't restore session after crash
        # Prevents "Restore Session?" dialogs in tests
        options.set_preference("browser.sessionstore.resume_from_crash", False)

        # ====================================================================
        # Security Settings (Testing-Specific)
        # ====================================================================
        # Allow mixed content (HTTP resources on HTTPS pages)
        # Note: Only use in testing environments
        # Some staging/dev environments may have mixed content
        # Firefox 127+ (June 2024) auto-upgrades images/video to HTTPS
        options.set_preference("security.mixed_content.block_active_content", False)

        # Optional: Also allow mixed display content (images, videos)
        # Uncomment if your test environment requires it
        # options.set_preference("security.mixed_content.block_display_content", False)

        # ====================================================================
        # Logging Configuration
        # ====================================================================
        # Enable console output to be captured by Selenium
        # Useful for debugging JavaScript errors in tests
        options.set_preference("devtools.console.stdout.content", True)

        return options