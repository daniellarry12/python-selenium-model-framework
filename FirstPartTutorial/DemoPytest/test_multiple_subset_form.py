from email import message
from selenium.webdriver.common.by import By

def test_lambdatest_simple_form_demo(driver):
    driver.get("https://www.lambdatest.com/selenium-playground/simple-form-demo")
    driver.find_element(By.XPATH, "//input[@id='user-message']"
        ).send_keys("Pytest is a test framework")
    driver.find_element(By.ID, "showInput").click()
    message = driver.find_element(By.ID, "message")
    driver.implicitly_wait(5)
    # assert message == "Pytest is a test framework"


