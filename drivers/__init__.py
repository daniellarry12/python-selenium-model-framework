"""
Driver Management Package

This package provides production-ready WebDriver management for Selenium tests.

Modules:
    browser_factory: Factory for creating WebDriver instances
    driver_manager: Lifecycle management for WebDriver instances
    browser_options: Browser-specific options (chrome, firefox, edge)

Usage:
    from drivers.driver_manager import DriverManager
    from config.environment_manager import get_config

    config = get_config('dev')
    manager = DriverManager('chrome', config, headless=True)
    driver = manager.driver
    # ... use driver ...
    manager.quit()
"""

from drivers.driver_manager import DriverManager
from drivers.browser_factory import BrowserFactory

__all__ = ['DriverManager', 'BrowserFactory']
