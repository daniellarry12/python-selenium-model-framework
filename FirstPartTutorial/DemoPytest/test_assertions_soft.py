from selenium.webdriver.common.by import By


class TestAssertions:

    def test4_lambdatest_radio(self, driver):
        driver.get("https://www.lambdatest.com/selenium-playground/radiobutton-demo")
        driver.find_element(By.XPATH, "//h4[contains(text(), 'Gender')]"
            "//following::input[@value='Male']").click()
        driver.find_element(By.XPATH, "//h4[contains(text(), 'Age')]"
            "//following::input[@value='15 - 50']").click()
        driver.find_element(By.XPATH,
            "//button[text()='Get values']").click()
        gender = driver.find_element(By.CSS_SELECTOR,
            ".genderbutton").text
        age_group = driver.find_element(By.CSS_SELECTOR,
            ".groupradiobutton").text
        assert gender == "Male", "Gender is not correct"
        # assert driver.title.__contains__("Selenium Grid Online") # this is not the more pythonic approach
        assert "Selenium Grid Online" in driver.title # this is the pythonic way
        assert "50" in age_group, "Age Group is not correct"

    
