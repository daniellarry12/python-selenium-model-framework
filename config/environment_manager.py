"""Environment Manager - Loads configuration based on selected environment"""

import os
import importlib
from dotenv import load_dotenv

load_dotenv()


def get_config(env_name: str = None):
    """
    Get configuration for the specified environment.

    Args:
        env_name: 'dev', 'staging', or 'prod'. Defaults to TEST_ENV from .env

    Returns:
        Configuration object with all settings
    """
    # Get environment name
    if env_name is None:
        env_name = os.getenv('TEST_ENV', 'dev')

    env_name = env_name.lower()

    # Load config file (dev.py, staging.py, or prod.py)
    try:
        config_module = importlib.import_module(f'config.environments.{env_name}')
    except ModuleNotFoundError:
        raise ValueError(f"Invalid environment: '{env_name}'. Valid: dev, staging, prod")

    # Load environment variables from .env
    prefix = env_name.upper() + "_"

    base_url = os.getenv(f"{prefix}BASE_URL")
    if not base_url:
        raise ValueError(f"{prefix}BASE_URL not found in .env")

    # Create simple config object
    class Config:
        # From .env
        BASE_URL = base_url
        API_URL = os.getenv(f"{prefix}API_URL", "")
        TEST_EMAIL = os.getenv(f"{prefix}TEST_EMAIL")
        TEST_PASSWORD = os.getenv(f"{prefix}TEST_PASSWORD")

        # From config file
        ENVIRONMENT = config_module.ENVIRONMENT
        IMPLICIT_WAIT = config_module.IMPLICIT_WAIT
        PAGE_LOAD_TIMEOUT = config_module.PAGE_LOAD_TIMEOUT
        LOG_LEVEL = config_module.LOG_LEVEL

    return Config()
