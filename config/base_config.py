"""
Base Configuration - Global values that DON'T change per environment.

This file contains configuration values that should be the same across
all environments (dev, staging, production). Environment-specific values
like URLs, credentials, and feature flags go in config/environments/.

"""

# ============================================================================
# Selenium Timeouts (same for all environments)
# ============================================================================
IMPLICIT_WAIT = 10  # Seconds to wait for elements to appear
PAGE_LOAD_TIMEOUT = 30  # Seconds to wait for page to load
SCRIPT_TIMEOUT = 30  # Seconds to wait for async scripts

# ============================================================================
# Browser Configuration
# ============================================================================
WINDOW_SIZE = (1920, 1080)  # Default window size
SUPPORTED_BROWSERS = ["chrome", "firefox", "edge"]

# ============================================================================
# Test Execution
# ============================================================================
MAX_RETRIES = 3  # Number of times to retry a failed test
RETRY_DELAY = 2  # Seconds to wait between retries

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
EXPLICIT_WAIT_TIMEOUT = 15  # Default timeout for explicit waits

# ============================================================================
# Performance
# ============================================================================
PARALLEL_WORKERS = 4  # Number of parallel test workers (for pytest-xdist)