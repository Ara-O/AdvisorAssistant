from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time


# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

try:
    # Open the website
    driver.get("https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/registration")
    # Wait for the page to load
    driver.implicitly_wait(3)

    browse_classes_button = driver.find_element(By.ID, "classSearch")
    browse_classes_button.click()
    
    driver.implicitly_wait(3)

    # Click the select button
    class_search_select = driver.find_element(By.ID, "select2-chosen-1")
    class_search_select.click()
    
    # Clear if there's anything on there, then type the semester and select the first result
    search_input = driver.find_element(by=By.ID,value="s2id_autogen1_search")
    search_input.clear()
    search_input.send_keys("Fall 2025")
    search_input.send_keys(Keys.RETURN)
    driver.implicitly_wait(5)
    
    drop_down=driver.find_element(by=By.ID,value="select2-results-1")
    first_option = drop_down.find_element(By.XPATH, ".//li[1]//div/div") 
    
    first_option.click()
    driver.implicitly_wait(5)
    continue_button = driver.find_element(by=By.ID,value="term-go")
    continue_button.click()
    
    driver.implicitly_wait(5)
    cookies = driver.get_cookies()

    print(cookies)

finally:
    # Close the driver
    driver.quit()