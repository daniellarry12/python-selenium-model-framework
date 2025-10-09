"""
Configuration manager for test environments.

Loads environment-specific settings from .env and combines them
with global settings from base_config.py.

Design:
- Environment-specific values (URLs, credentials) → .env file
- Global values (timeouts, browser settings) → base_config.py
- Immutable configuration via frozen dataclass
- Automatic caching via @lru_cache
"""

import os
from dataclasses import dataclass
from functools import lru_cache
from dotenv import load_dotenv
from config import base_config


@dataclass(frozen=True)
class EnvironmentConfig:
    """
    Immutable configuration for a test environment.

    """
    environment: str
    base_url: str
    test_email: str
    test_password: str
    implicit_wait: int
    page_load_timeout: int


@lru_cache(maxsize=3)
def get_config(env_name: str | None = None) -> EnvironmentConfig:
    """
    Load configuration for the specified environment.

    Args:
        env_name: Environment name (dev, staging, prod).
                  If None, reads TEST_ENV from .env.
                  Defaults to 'dev' if TEST_ENV not set.

    Returns:
        Immutable EnvironmentConfig instance with all settings.

    Example:
        >>> config = get_config('staging')
        >>> print(config.base_url)
        >>> print(config.implicit_wait)  # From base_config.py
    """
    # Load .env file (only on first call, dotenv caches internally)
    load_dotenv()

    # Get environment name
    env_name = (env_name or os.getenv('TEST_ENV', 'dev')).lower().strip()

    # Build environment variable prefix (DEV_, STAGING_, PROD_)
    prefix = f"{env_name.upper()}_"

    # Load environment-specific variables from .env
    base_url = os.getenv(f"{prefix}BASE_URL")
    test_email = os.getenv(f"{prefix}TEST_EMAIL")
    test_password = os.getenv(f"{prefix}TEST_PASSWORD")

    # Validate that all required variables exist
    if not all([base_url, test_email, test_password]):
        # Build helpful error message showing exactly what's missing
        missing = [
            var_name for var_name, var_value in [
                (f"{prefix}BASE_URL", base_url),
                (f"{prefix}TEST_EMAIL", test_email),
                (f"{prefix}TEST_PASSWORD", test_password),
            ] if not var_value
        ]
        raise ValueError(
            f"Missing required environment variables for '{env_name}' environment: "
            f"{', '.join(missing)}. Please check your .env file."
        )

    # Create and return immutable configuration
    # Environment-specific values from .env, global values from base_config.py
    # Note: base_url, test_email, test_password are guaranteed to be str (validated above)
    return EnvironmentConfig(
        environment=env_name,
        base_url=base_url,  # type: ignore[arg-type]
        test_email=test_email,  # type: ignore[arg-type]
        test_password=test_password,  # type: ignore[arg-type]
        # Global configuration from base_config.py
        implicit_wait=base_config.IMPLICIT_WAIT,
        page_load_timeout=base_config.PAGE_LOAD_TIMEOUT,
    )
