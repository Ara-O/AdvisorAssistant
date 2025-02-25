from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
CORS(app=app)

def formatResults(courses):
    formattedResult = []
    for course in courses:
        course_dict = {}
        course_dict["course_name"] = course["courseTitle"]
        course_dict["credits"] = course["creditHours"]
        course_dict["current_enrollment"] = course["enrollment"]
        course_dict["course_id"] = course["id"]
        course_dict["section"] = course["sequenceNumber"]
        course_dict["subject"] = course["subject"]
        course_dict["course_number"] = course["courseNumber"]
        course_dict["course_description"] = course["subjectDescription"]

        meetings = course["meetingsFaculty"]

        # TODO: Some have multiple of this for multiple meeting times
        if len(meetings) > 0:
            meetings = meetings[0]
            course_dict["meeting_begin_time"] = meetings["meetingTime"]["beginTime"]
            course_dict["meeting_end_time"] = meetings["meetingTime"]["endTime"]
            course_dict["meeting_hours_weekly"] = meetings["meetingTime"]["hoursWeek"]
            course_dict["monday"] = meetings["meetingTime"]["monday"]
            course_dict["tuesday"] = meetings["meetingTime"]["tuesday"]
            course_dict["wednesday"] = meetings["meetingTime"]["wednesday"]
            course_dict["thursday"] = meetings["meetingTime"]["thursday"]
            course_dict["friday"] = meetings["meetingTime"]["friday"]
            course_dict["saturday"] = meetings["meetingTime"]["saturday"]
            course_dict["sunday"] = meetings["meetingTime"]["sunday"]
            course_dict["start_date"] = meetings["meetingTime"]["startDate"]
            course_dict["end_date"] = meetings["meetingTime"]["endDate"]
            course_dict["building"] = meetings["meetingTime"]["building"]
            course_dict["campus_description"] = meetings["meetingTime"]["campusDescription"]
            course_dict["meeting_type_description"] = meetings["meetingTime"]["meetingTypeDescription"]

        formattedResult.append(course_dict)
        
    return formattedResult
        
@app.route('/health', methods=['GET'])
def health():
    return "healthy :D"

            

@app.route('/course_proxy', methods=['GET'])
def proxy():
    API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/getTerms" 
    try:
        # Forward the request to the actual API
        response = requests.get(API_URL, params={
            "searchTerm": "",  # Keep it empty or add a search keyword
            "offset": 1,       # Start from the first result
            "max": 10, 
        })
        
        # Return the API response as JSON
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fetch_courses", methods=['GET'])
def fetch_course():
    print("Fetching courses....")
    term_code = request.args.get("term_code")
    term_name = request.args.get("term_name")
    
    term_name = term_name.replace(" (View Only)", "")
    page_size = 10
    max_page_size = 500
    
    API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"

    if not request.args.get("jsessionid"):
        # Set up Chrome WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")  # Use "--headless" if this causes issues
        chrome_options.add_argument("--no-sandbox")  # Recommended for cloud environments
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--disable-gpu") 
        chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
        driver = webdriver.Chrome(options=chrome_options)

        print("Launching selenium...")
        try:
            # Open the website
            driver.get("https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/registration")
            # Wait for the page to load
            driver.implicitly_wait(3)
            print("On page")

            browse_classes_button = driver.find_element(By.ID, "classSearch")
            browse_classes_button.click()
            print("Clicked class search")
            
            driver.implicitly_wait(3)

            # Click the select button
            class_search_select = driver.find_element(By.ID, "select2-chosen-1")
            class_search_select.click()
            print('Clicked selected chosen 1')
            
            # Clear if there's anything on there, then type the semester and select the first result
            search_input = driver.find_element(by=By.ID,value="s2id_autogen1_search")
            search_input.clear()
            search_input.send_keys(term_name)
            search_input.send_keys(Keys.RETURN)
         
            print(f"Input field value: {search_input.get_attribute('value')}")
            print("Clicked search result")
            
     
            dropdown = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//ul[contains(@class, 'select2-results')]"))
            )
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'select2-results')]//div"))
            )
            # option.click()
            
            
            results = dropdown.find_elements(By.XPATH, "//li")  # Or adjust XPath based on the actual dropdown items
            print(f"Number of results in dropdown: {len(results)}")
            if len(results) > 0:
                print(f"First result text: {results[0].text}")
            else:
                print("No results found")

            option.click()
            print("Clicked dropdown option")
            # drop_down=driver.find_element(by=By.ID,value="select2-results-1")
            # first_option = drop_down.find_element(By.XPATH, ".//li[1]//div/div") 
            # first_option.click()
            print("clicked first result 1")
            driver.implicitly_wait(5)
            continue_button = driver.find_element(by=By.ID,value="term-go")
            continue_button.click()
            
            print("Clicked go")
            driver.implicitly_wait(5)
            cookies = driver.get_cookies()

            print(cookies)

        finally:
            # Close the driver
            driver.quit()
        
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

        AWSALB = cookie_dict.get("AWSALB", "")
        AWSALBCORS = cookie_dict.get("AWSALBCORS", "")
        JSESSIONID = cookie_dict.get("JSESSIONID", "")
    else:
        JSESSIONID = request.args.get("jsessionid")
        AWSALB = request.args.get("awsalb")
        AWSALBCORS = request.args.get("awsalbcors")
    # Print values
    print("AWSALB:", AWSALB)
    print("AWSALBCORS:", AWSALBCORS)
    print("JSESSIONID:", JSESSIONID)
    
    cookies = {
            "AWSALB":  AWSALB,
            "AWSALBCORS": AWSALBCORS,
            "JSESSIONID":  JSESSIONID,
            # "taxitag_main": "v_id:0193db54b63500803a61c3340d7805046005b00900bd0$_sn:26$_se:3$_ss:0$_st:1740268426041$dc_visit:26$ses_id:1740266596186%3Bexp-session$_pn:3%3Bexp-session$dc_event:3%3Bexp-session$tag_session_91:1%3Bexp-session"
    }
    
    params = {
        "txt_term": str(term_code),
        "startDatepicker": "",
        "endDatepicker": "",
        "uniqueSessionId": "gro1j1740356345340",  # Generate a new session ID
        "sortColumn": "subjectDescription",
        "sortDirection": "asc",
        "enrollmentDisplaySettings": ""
    }
    
    try:
        params.update({
            'pageOffset': 0,
            "pageMaxSize": 10
        })
                
        # Fetch total count
        response = requests.get(API_URL, params=params, cookies=cookies)
        print(response)
        
        response_json = response.json()
        
        total_courses = response_json["totalCount"]
        print(f"Total courses: {total_courses}")
        
        # Start fetching the actual courses        
        all_results = [] 
        for i in range((total_courses//max_page_size) + 1):
            params.update({
                'pageOffset': i * max_page_size,
                "pageMaxSize": max_page_size
            })
            response = requests.get(API_URL, params=params, cookies=cookies)
            
            response_json = response.json()
            
            all_results.extend(response_json["data"])
            
        print("ALl results", len(all_results))
        
        with open("course_data.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=4)
        
    
        print(type(all_results))
        results = formatResults(all_results)
        # Return the API response as JSON
        return results, response.status_code

    except requests.exceptions.RequestException as e:
        print(e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  

