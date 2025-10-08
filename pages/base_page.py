from selenium import webdriver
from selenium.webdriver.common.by import By
class BasePage:

    # Class constructor
    def __init__(self, driver):
        self.driver = driver
    
    """Common methods"""
    def find(self, *locator):
        return self.driver.find_element(*locator)
    
    def click(self, locator):
        self.find(*locator).click()

    def set(self, locator, value):
        self.find(*locator).clear()
        self.find(*locator).send_keys(value)

    def get_text(self, locator):
        return self.find(*locator).text
    
    def get_title(self):
        return self.driver.title
    
    """Methods for elements"""
    def click_right_menu_page(self, page_name):
        page = By.XPATH, "//aside[@id='column-right']//a[text()=' "+ page_name +"']"
        self.click(page)

    # Below method allow us to click pages from the rigtside menu, check if page is visible & more actions
    def page(self, page_name):
        return By.XPATH, "//aside[@id='column-right']//a[text()=' "+ page_name +"']"