import os


class TestData:
    """Test data configuration using environment variables with fallback defaults"""

    # URL is now managed via BASE_URL environment variable in conftest.py
    # Keeping this for backward compatibility if needed
    url = os.getenv(
        "BASE_URL",
        "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    )

    # Test credentials from environment variables
    email = os.getenv("TEST_EMAIL", "pytesttutorial@gmail.com")
    password = os.getenv("TEST_PASSWORD", "Jahlove1912$")