"""
Environment Configuration Manager

Loads environment-specific settings from config files and .env variables.

Usage:
    from config.environment_manager import get_config

    config = get_config('staging')
    driver.implicitly_wait(config.implicit_wait)
    driver.get(config.base_url)
"""

import os
import importlib
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass(frozen=True)  # frozen=True makes it immutable (can't change accidentally)
class EnvironmentConfig:
    """
    Configuration for a specific environment.

    Attributes:
        environment: Environment name (dev, staging, prod)
        base_url: Application URL
        api_url: API URL (optional)
        test_email: Test account email
        test_password: Test account password
        implicit_wait: Selenium implicit wait in seconds
        page_load_timeout: Page load timeout in seconds
        log_level: Logging level (DEBUG, INFO, WARNING)
    """
    # From .env
    environment: str
    base_url: str
    api_url: str
    test_email: str
    test_password: str

    # From config file (dev.py, staging.py, prod.py)
    implicit_wait: int
    page_load_timeout: int
    log_level: str


# Cache to avoid loading config multiple times (singleton pattern)
_config_cache: dict[str, EnvironmentConfig] = {}
_dotenv_loaded = False


def get_config(env_name: Optional[str] = None) -> EnvironmentConfig:
    """
    Get configuration for specified environment.

    Args:
        env_name: 'dev', 'staging', or 'prod'. If None, reads from TEST_ENV in .env

    Returns:
        EnvironmentConfig object with all settings

    Raises:
        ValueError: If environment is invalid or required variables missing

    Example:
        >>> config = get_config()  # Uses TEST_ENV from .env
        >>> config = get_config('staging')  # Override to staging
        >>> print(config.base_url)
    """
    global _dotenv_loaded

    # Load .env file once (lazy loading - not on module import)
    if not _dotenv_loaded:
        load_dotenv()
        _dotenv_loaded = True

    # Get environment name
    if env_name is None:
        env_name = os.getenv('TEST_ENV', 'dev')

    env_name = env_name.lower().strip()

    # Return cached config if already loaded (performance optimization)
    if env_name in _config_cache:
        return _config_cache[env_name]

    # Load config module (dev.py, staging.py, or prod.py)
    try:
        config_module = importlib.import_module(f'config.environments.{env_name}')
    except ModuleNotFoundError:
        raise ValueError(
            f"Invalid environment: '{env_name}'. "
            f"Valid options: dev, staging, prod"
        )

    # Build prefix for env variables (DEV_, STAGING_, PROD_)
    prefix = env_name.upper() + "_"

    # Get required variables from .env (raise error if missing)
    base_url = os.getenv(f"{prefix}BASE_URL")
    test_email = os.getenv(f"{prefix}TEST_EMAIL")
    test_password = os.getenv(f"{prefix}TEST_PASSWORD")

    # Validate critical variables exist
    if not base_url:
        raise ValueError(
            f"{prefix}BASE_URL not found in .env file. "
            f"Please check your .env configuration."
        )
    if not test_email:
        raise ValueError(f"{prefix}TEST_EMAIL not found in .env file.")
    if not test_password:
        raise ValueError(f"{prefix}TEST_PASSWORD not found in .env file.")

    # Create config object
    config = EnvironmentConfig(
        environment=env_name,
        base_url=base_url,
        api_url=os.getenv(f"{prefix}API_URL", ""),  # Optional, default empty
        test_email=test_email,
        test_password=test_password,
        implicit_wait=config_module.IMPLICIT_WAIT,
        page_load_timeout=config_module.PAGE_LOAD_TIMEOUT,
        log_level=config_module.LOG_LEVEL,
    )

    # Cache for future calls
    _config_cache[env_name] = config

    return config


def reset_config() -> None:
    """Clear cached configs (useful for testing only)."""
    global _config_cache, _dotenv_loaded
    _config_cache.clear()
    _dotenv_loaded = False
