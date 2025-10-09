"""
Browser Options Package

Provides production-ready options for different browsers.

Each browser has its own options builder:
    - ChromeOptionsBuilder: Chrome/Chromium options
    - FirefoxOptionsBuilder: Firefox options
    - EdgeOptionsBuilder: Edge options

Usage:
    from drivers.browser_options.chrome_options import ChromeOptionsBuilder

    options = ChromeOptionsBuilder.build(headless=True)
    driver = webdriver.Chrome(options=options)
"""

from drivers.browser_options.chrome_options import ChromeOptionsBuilder
from drivers.browser_options.firefox_options import FirefoxOptionsBuilder
from drivers.browser_options.edge_options import EdgeOptionsBuilder

__all__ = ['ChromeOptionsBuilder', 'FirefoxOptionsBuilder', 'EdgeOptionsBuilder']
