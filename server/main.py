import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
from selenium.webdriver.support import expected_conditions as EC
from pdfdataextractor import process_student_profile

load_dotenv()
app = Flask(__name__)
CORS(app=app)

def formatResult(course):
    course_dict = {}
    course_dict["course_name"] = course["courseTitle"]
    course_dict["credits"] = course["creditHours"]
    course_dict["course_reference_number"] = course["courseReferenceNumber"]
    course_dict["current_enrollment"] = course["enrollment"]
    course_dict["course_id"] = course["id"]
    course_dict["section"] = course["sequenceNumber"]
    course_dict["subject"] = course["subject"]
    course_dict["course_number"] = course["courseNumber"]
    course_dict["course_description"] = course["subjectDescription"]
    course_dict["attributes"] = course["sectionAttributes"]
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
    
    return course_dict


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
        course_dict["attributes"] = course["sectionAttributes"]
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

def fetch_cookies(term_name):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")  # Recommended for cloud environments
    chrome_options.add_argument("--headless=new")  # Use "--headless" if this causes issues
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--enable-logging")
    driver = webdriver.Chrome(options=chrome_options)

    print("Launching selenium...")
    
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
        search_input.send_keys(term_name)
        search_input.send_keys(Keys.RETURN)
   
        dropdown = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//ul[contains(@class, 'select2-results')]"))
        )
            
        time.sleep(5)
            
        results = dropdown.find_elements(By.XPATH, "//li")  # Or adjust XPath based on the actual dropdown items

        if len(results) > 0:
            print(f"First result text: {results[0].text}")
        else:
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

        driver.implicitly_wait(5)
            
        continue_button = driver.find_element(by=By.ID,value="term-go")
        continue_button.click()
            
        driver.implicitly_wait(5)
        cookies = driver.get_cookies()

        return cookies
    finally:
        # Close the driver
        driver.quit()
        
    
@app.route("/fetch_courses", methods=['GET'])
def fetch_course():
    print("Fetching courses....")
    term_code = request.args.get("term_code")
    term_name = request.args.get("term_name")
    use_cache = request.args.get("use_cache")
    
    term_name = term_name.replace(" (View Only)", "")
    max_page_size = 500
    
    API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"
    
    term_title = term_name.split(" ")
    term_json_file = "".join(term_title).lower() + ".json"
    
    print(f"Using Cache: {use_cache}")
    if json.loads(use_cache):
        try:
            with open(term_json_file, "r") as file:
                data = json.load(file)
                results = formatResults(data)
                return results, 200

        except FileNotFoundError:
            print('File not found, SO NO CACHE EXISTS YET ')
    
    # 
    if not request.args.get("jsessionid"):
        cookies = fetch_cookies(term_name=term_name)
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        AWSALB = cookie_dict.get("AWSALB", "")
        AWSALBCORS = cookie_dict.get("AWSALBCORS", "")
        JSESSIONID = cookie_dict.get("JSESSIONID", "")
    else:
        JSESSIONID = request.args.get("jsessionid")
        AWSALB = request.args.get("awsalb")
        AWSALBCORS = request.args.get("awsalbcors")
    

    cookies = {
            "AWSALB":  AWSALB,
            "AWSALBCORS": AWSALBCORS,
            "JSESSIONID":  JSESSIONID,
    }
    
    params = {
        "txt_term": str(term_code),
        "startDatepicker": "",
        "endDatepicker": "",
        "uniqueSessionId": "gro1j1740356345340",
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
            
        print("All results: ", len(all_results))
        
        with open(term_json_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=4)
        
        results = formatResults(all_results)

        return results, response.status_code

    except requests.exceptions.RequestException as e:
        print(e)
        return jsonify({"error": str(e)}), 500

MAILGUN_API_URL = os.getenv("MAILGUN_API_URL")
api_key = os.getenv("MAILGUN_API_KEY")

@app.route("/send_feedback", methods=['POST'])
def send_feedback():
    try:
        feedback_message = request.json["feedback_message"]
        print(feedback_message)
        
        resp = requests.post(MAILGUN_API_URL, auth=("api", api_key),
                             data={"from": "oladipoeyiara@gmail.com",
                                   "to": "oladipoeyiara@gmail.com", "subject": "Course Viewer Feedback", "text": feedback_message})
        
        # print(resp)
        return "Feedback sent successfully", 200
    except Exception as ex: 
        print(ex)
        return "Error", 500

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload_degree_evaluation", methods=['POST'])
def upload_degree_evaluation():
    print("Uploaded degree evaluation")
    
    if 'degree_eval' not in request.files:
            return "File not found", 500
    
    file = request.files['degree_eval']
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    file.save(file_path)
    
    requirements = process_student_profile(file_path)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return requirements, 200


def extract_course_code(text):
    """Extracts course code from text using regex."""
    match = re.search(r'\b[A-Z]+\d\b', text)  
    return match.group(0) if match else None

def find_matching_object(json_data, attribute_code):
    # print(f"Looking for attribute code {attribute_code}")
    matching_attrs = []
    """Finds the object in json_data where sectionAttributes contains the attribute_code."""
    for obj in json_data:  # Iterate through list of objects
        for section in obj.get("sectionAttributes", []):  # Check sectionAttributes in each object
            if section.get("code") == attribute_code or (attribute_code in section.get("code")):
                # print("match found yay")
                matching_attrs.append(obj)  # Return the full object containing the match
    return matching_attrs  

@app.route("/start-assistant", methods=['POST'])
def startAdvisorAssistant():
    request_data = request.json
    
    requirements_satisfied = request_data["requirements_satisfied"]
    requirements_not_satisfied = request_data["requirements_not_satisfied"]

    # TODO - MAKE THIS BASED ON THE TERM
    with open("fall2025.json", "r") as file:
        data = json.load(file) 

    course_matched_data = {}
    # Loop through all the satisfied requirements and find all the course times 
    for req_outer in requirements_not_satisfied:
        for req in req_outer["courses"]:
            # Extract the requirements since one can have multiple under it
            courses = re.findall(r"[A-Z]{2,4} \d{4}", req)
            course_matched_data[req] = []
            
            attr_match = re.search(r'\b[A-Z]{1,2}\d\b', req)
        
            if attr_match:
                attr = attr_match.group(0)
                matched_object = find_matching_object(data, attr)
                if len(matched_object) > 0:
                    course_matched_data[req].extend(formatResults(matched_object))

            for course in courses:
                # Find course in JSON
                # print(course)
                subject = course.split()[0]
                course_number = course.split()[1]
                
                match = next(
                    (course for course in data if course["subject"] == subject and course["courseNumber"] == course_number),
                    None
                )
                
                # ideal: Find all the prerequisites as well and display that to the user
                # might be a lot if the user is a new student, so fetching prerequisites can be done dynamically for an added course
                # then it'll check if the pre-requisites are in the list of the course the user has already taken
                if match:
                    # print(match)
                    course_matched_data[req].append(formatResult(match))
                
    
    return course_matched_data, 200
    
def tokenize_prerequisites(raw_texts):
    """Tokenizes the prerequisites text into meaningful units."""
    tokens = []
    course_pattern = re.compile(r"Course or Test:\s*([\w\s\/]+)\s+(\d+)")
    grade_pattern = re.compile(r"Minimum Grade of ([A-FP])")

    for text in raw_texts:
        text = text.replace("\n", " ").strip()  # Flatten text

        if text in ("or", "and", "(", ")"):
            tokens.append(text)
            continue

        course_match = course_pattern.search(text)
        grade_match = grade_pattern.search(text)

        if course_match:
            subject, course_number = course_match.groups()
            min_grade = grade_match.group(1) if grade_match else None
            tokens.append({"subject": subject.strip(), "course_number": course_number, "min_grade": min_grade})

    return tokens

def parse_tokens(tokens):
    """Recursively parses tokens into a nested structure."""
    stack = []
    
    while tokens:
        token = tokens.pop(0)

        if token == "(":
            # Start a new group
            sub_expr = parse_tokens(tokens)
            stack.append(sub_expr)

        elif token == ")":
            # End the current group
            return stack

        elif token in ("or", "and"):
            stack.append(token)

        else:
            # Course object
            stack.append(token)

    return stack

def parse_prerequisites(html):
    """Extracts and structures prerequisite information from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the prerequisites section
    section = soup.find("section", {"aria-labelledby": "preReqs"})
    if not section:
        return "No prerequisite section found."

    table = section.find("table")
    if not table:
        return "No prerequisite information available."

    # Extract text from all <pre> elements
    raw_texts = [pre.get_text(strip=True) for pre in table.find_all("pre")]

    # Tokenize and parse
    tokens = tokenize_prerequisites(raw_texts)
    parsed_structure = parse_tokens(tokens)

    return parsed_structure

# def parse_prerequisites(html):
#     """Parses prerequisites from HTML and extracts course requirements with relationships."""
#     soup = BeautifulSoup(html, "html.parser")

#     # Find the prerequisites section
#     section = soup.find("section", {"aria-labelledby": "preReqs"})
#     if not section:
#         return "No prerequisite section found."

#     table = section.find("table")
#     if not table:
#         return "No prerequisite information available."

#     # Extract text from all <pre> elements
#     raw_texts = [pre.get_text(strip=True) for pre in table.find_all("pre")]

#     # Prepare a list to store structured prerequisites
#     prerequisites = []
#     current_group = []
#     logical_operator = None

#     # Regex patterns
#     course_pattern = re.compile(r"Course or Test:\s*([\w\s\/]+)\s+(\d+)")
#     grade_pattern = re.compile(r"Minimum Grade of ([A-F])")
    
#     for text in raw_texts:
#         text = text.replace("\n", " ")  # Flatten multi-line texts

#         if text in ("or", "and"):  # Handle logical operators
#             if current_group:
#                 prerequisites.append({"courses": current_group, "relation": logical_operator})
#                 current_group = []
#             logical_operator = text
#             continue
        
#         if "(" in text or ")" in text:  # Handle grouping parentheses
#             continue

#         # Extract course name, number, and grade
#         course_match = course_pattern.search(text)
#         grade_match = grade_pattern.search(text)

#         if course_match:
#             subject, course_number = course_match.groups()
#             min_grade = grade_match.group(1) if grade_match else None
#             current_group.append({"subject": subject.strip(), "course_number": course_number, "min_grade": min_grade})

#     # Append last group
#     if current_group:
#         prerequisites.append({"courses": current_group, "relation": logical_operator})

#     return prerequisites

def parse_requirements(html, req_type):
    """Parses prerequisites or corequisites from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the section based on the req_type (preReqs or coReqs)
    section = soup.find("section", {"aria-labelledby": req_type})
    
    if not section:
        return f"No {req_type} section found."

    # Check if there is a table (meaning there are requirements)
    table = section.find("table")
    if not table:
        return f"No {req_type.replace('Reqs', ' reqs')} information available."

    # If it's a prerequisite section
    if req_type == "preReqs":
        preq_texts = []
        for pre in table.find_all("pre"):
            text = pre.get_text(strip=True).replace("\n", " ")  # Clean formatting
            preq_texts.append(text)
        return preq_texts

    # If it's a corequisite section
    elif req_type == "coReqs":
        coreqs = []
        for row in table.find("tbody").find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 3:
                subject, course_number, title = [col.get_text(strip=True) for col in cols]
                coreqs.append(f"{subject} {course_number}: {title}")
        return coreqs
    
@app.route("/check_course_validity", methods=['POST'])
def check_course_validity():
    req = request.json
    
    requirements_satisfied = req["requirements_satisfied"]
    course = req["course"]
    
    # Get course prerequisites 
    # TODO: Make based on selected term
    
    print(course)
    url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"

    session = requests.Session()  # Maintain session
    response = session.get(url)

    cookies = session.cookies.get_dict()  # Extract cookies

    # cookies = fetch_cookies("Fall 2025")
    # cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
     
    AWSALB = cookies.get("AWSALB", "")
    AWSALBCORS = cookies.get("AWSALBCORS", "")
    JSESSIONID = cookies.get("JSESSIONID", "")

    API_URL_PREREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"
    API_URL_COREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getCorequisites"

    # Change term, could access term code from the course itself
    params = {
        "term": "202610",
        "courseReferenceNumber": course['course_reference_number']
    }
    
    cookies = {
            "AWSALB":  AWSALB,
            "AWSALBCORS": AWSALBCORS,
            "JSESSIONID":  JSESSIONID,
    }
    
    prereqs_response = requests.post(API_URL_PREREQS, params=params, cookies=cookies)
    coreqs_response = requests.post(API_URL_COREQS, params=params, cookies=cookies)

    course_prereqs = prereqs_response.text
    course_coreqs = coreqs_response.text
    
    prerequisites =  parse_prerequisites(course_prereqs)
    corequisites = parse_requirements(course_coreqs, "coReqs")
    
    print("Prereqs", prerequisites)
    print("Coreqs", corequisites)

    return  jsonify({
        "prerequisites": prerequisites,
        "corequisites": corequisites }), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  

