import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()

@pytest.fixture(autouse=True)
def start_automatic_fixture():
    print("Start Test With Automatic Fixture")


@pytest.fixture()
def setup_teardown():
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")
    driver.find_element(By.ID, "input-email").send_keys("pytesttutorial@gmail.com")
    driver.find_element(By.ID, "input-password").send_keys("Jahlove1912$")
    driver.find_element(By.XPATH, "//input[@value='Login']").click()
    print("Log in")
    yield
    driver.find_element(By.PARTIAL_LINK_TEXT, "Logout").click()
    print("Log out")


def test1_order_history_title(setup_teardown):
    driver.find_element(By.PARTIAL_LINK_TEXT, "Order").click()
    assert driver.title == "Order History"
    print("Test 1 is complete")

def test2_change_password_title(setup_teardown):
    driver.find_element(By.PARTIAL_LINK_TEXT, "Password").click()
    assert driver.title == "Change Password"
    print("Test 2 is complete")