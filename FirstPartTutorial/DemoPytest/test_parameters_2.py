
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



    
@pytest.mark.usefixtures("initialize_driver")
class BaseClass:
   pass

class Test_Driver(BaseClass):
   def test_multiple_browsers(self):
      self.driver.get("https://www.lambdatest.com/selenium-playground/")
      time.sleep(1)
      wait = WebDriverWait(self.driver, 10)
      header_element = wait.until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Selenium Playground')]"))
      )
      header = header_element.text
      print(f"Header: {header}")
      assert header == "Selenium Playground"
      



    