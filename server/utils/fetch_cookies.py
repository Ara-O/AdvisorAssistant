from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
import time

def fetch_cookies(term_name: str):
    # Define the environment for the scraper
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")  # Recommended for cloud environments
    chrome_options.add_argument("--headless=new")  # Use "--headless" if this causes issues
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--enable-logging")
    
    service = Service(executable_path="./chromedriver-linux64/chromedriver")
    
    # Defined in the render-build.sh
    chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/chrome"
    
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("Launching selenium...")
    
    try:
        # Open the website
        driver.get("https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/registration")
        
        # Wait for the page to load
        driver.implicitly_wait(1)

        browse_classes_button = driver.find_element(By.ID, "classSearch")
        browse_classes_button.click()            
        driver.implicitly_wait(1)

        # Click the select button
        class_search_select = driver.find_element(By.ID, "select2-chosen-1")
        class_search_select.click()
            
        # Clear if there's anything on there, then type the semester and select the first result
        search_input = driver.find_element(by=By.ID,value="s2id_autogen1_search")
        search_input.clear()
        search_input.send_keys(term_name)
        search_input.send_keys(Keys.RETURN)
   
        dropdown = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//ul[contains(@class, 'select2-results')]"))
        )
            
        time.sleep(1)
            
        results = dropdown.find_elements(By.XPATH, "//li")  

        if len(results) == 0:
            print("No results found")

        try:
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'select2-results')]//div"))
            )
            option.click()
            
        except StaleElementReferenceException:
            # Re-find the element if it went stale
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'select2-results')]//div"))
            )
 
            driver.execute_script("arguments[0].click();", option)

        driver.implicitly_wait(1)
            
        continue_button = driver.find_element(by=By.ID,value="term-go")
        continue_button.click()
            
        driver.implicitly_wait(1)
        cookies = driver.get_cookies()

        return cookies
    except Exception as e:
        print('There was an error fetching the cookies')
        print(e)
        return {}
    finally:
        # Close the driver
        driver.quit()
        
    