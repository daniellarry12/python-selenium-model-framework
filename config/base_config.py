"""
Base Configuration - Global values that DON'T change per environment.

This file contains configuration values that should be the same across
all environments (dev, staging, production). Environment-specific values
like URLs, credentials, and feature flags go in config/environments/.

"""

from enum import Enum


class WaitTime(Enum):
    """
    Usage:
        >>> from config.base_config import WaitTime
        >>> login_page.is_displayed(locator, timeout=WaitTime.SHORT.value)
        >>> page.wait_for_url_contains("/dashboard", timeout=WaitTime.DEFAULT.value)
    """
    # Quick visibility checks (buttons, error messages)
    SHORT = 5

    # Standard timeout for most elements and operations
    DEFAULT = 10

    # Medium waits (AJAX calls, animations, dynamic content)
    MEDIUM = 20

    # Heavy operations (page loads, API calls, file processing)
    LONG = 30

    # Very slow operations (large file uploads, batch jobs)
    EXTRA_LONG = 60


# ============================================================================
# Selenium Timeouts (backward compatibility + derived from Enum)
# ============================================================================
IMPLICIT_WAIT = WaitTime.DEFAULT.value  # Seconds to wait for elements to appear
PAGE_LOAD_TIMEOUT = WaitTime.LONG.value  # Seconds to wait for page to load
EXPLICIT_WAIT_TIMEOUT = WaitTime.DEFAULT.value  # Default timeout for explicit waits

# ============================================================================
# Browser Configuration
# ============================================================================
WINDOW_SIZE = (1920, 1080)  # Default window size

# ============================================================================
# Reporting & Debugging
# ============================================================================
SCREENSHOT_ON_FAILURE = True  # Take screenshot when test fails
SCREENSHOT_DIR = "screenshots"  # Directory to save screenshots
VIDEO_RECORDING = False  # Enable video recording (requires additional setup)

# ============================================================================
# Wait Strategies
# ============================================================================
POLLING_INTERVAL = 0.5  # Seconds between element visibility checks

# ============================================================================
# Performance
# ============================================================================
PARALLEL_WORKERS = 4  # Number of parallel test workers (for pytest-xdist)