
import pytest

@pytest.mark.sanity
@pytest.mark.smoke
def test1_lambdatest_playground(driver):
    driver.get("https://www.lambdatest.com/selenium-playground/")
    print(f"Page title is: {driver.title}")

@pytest.mark.regression
def test2_lambdatest_ecommerce(driver):
    driver.get("https://ecommerce-playground.lambdatest.io/")
    print(f"The page title is {driver.title}")

@pytest.mark.integration
def testRexWebsite(driver):
    driver.get("https://rexjones2.com")
    print("Title: ", driver.title)

@pytest.mark.integration
def test_google(driver):
    driver.get("https://google.com")
    print("Title: ", driver.title)
    