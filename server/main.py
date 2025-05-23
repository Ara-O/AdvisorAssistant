import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import requests
import time
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from pdfdataextractor import process_student_profile
from course_scheduler.fetch_course_with_subject_and_number import fetch_courses_with_subject_and_number_blueprint
from course_scheduler.fetch_all_terms import fetch_all_terms_blueprint
from course_scheduler.fetch_courses import fetch_courses_blueprint
# Load the variables in the .env file
load_dotenv()

app = Flask(__name__)

CORS(app=app, origins=["http://localhost:5173"])

app.register_blueprint(fetch_courses_with_subject_and_number_blueprint)
app.register_blueprint(fetch_all_terms_blueprint)
app.register_blueprint(fetch_courses_blueprint)

@app.route('/health', methods=['GET'])
def health():
    return "The app is running!"

# MAILGUN_API_URL = os.getenv("MAILGUN_API_URL")
# api_key = os.getenv("MAILGUN_API_KEY")

# @app.route("/send_feedback", methods=['POST'])
# def send_feedback():
#     try:
#         feedback_message = request.json["feedback_message"]
#         print(feedback_message)
        
#         resp = requests.post(MAILGUN_API_URL, auth=("api", api_key),
#                              data={"from": "oladipoeyiara@gmail.com",
#                                    "to": "oladipoeyiara@gmail.com", "subject": "Course Viewer Feedback", "text": feedback_message})
        
#         # print(resp)
#         return "Feedback sent successfully", 200
#     except Exception as ex: 
#         print(ex)
#         return "Error", 500

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/upload_degree_evaluation", methods=['POST'])
# def upload_degree_evaluation():
#     print("Uploaded degree evaluation")
    
#     if 'degree_eval' not in request.files:
#             return "File not found", 500
    
#     file = request.files['degree_eval']
    
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
#     file.save(file_path)
    
#     requirements = process_student_profile(file_path)
    
#     # print(requirements)
    
#     # with open("fall2025.json", "r") as file:
#     #     data = json.load(file) 
#     #     for req in requirements['requirements_satisfied']:
#     #         req['attributes_satisfied'] = []
#     #         # found_attributes = False
#     #         for full_course in data:
#     #             if f"{full_course['subject']} {full_course['courseNumber']}" == req['course']:
#     #                 for attr in full_course['sectionAttributes']:
#     #                     req['attributes_satisfied'].append(str(attr['code']).replace("KA", ""))
#     #                 break
    
#     # After processing, delete the file
#     if os.path.exists(file_path):
#         os.remove(file_path)
    
#     return requirements, 200


# def extract_course_code(text):
#     """Extracts course code from text using regex."""
#     match = re.search(r'\b[A-Z]+\d\b', text)  
#     return match.group(0) if match else None

# def find_matching_object(json_data, attribute_code):
#     # print(f"Looking for attribute code {attribute_code}")
#     matching_attrs = []
#     """Finds the object in json_data where sectionAttributes contains the attribute_code."""
#     for obj in json_data:  # Iterate through list of objects
#         for section in obj.get("sectionAttributes", []):  # Check sectionAttributes in each object
#             if section.get("code") == attribute_code or (attribute_code in section.get("code")):
#                 # print("match found yay")
#                 matching_attrs.append(obj)  # Return the full object containing the match
#     return matching_attrs  

# @app.route("/start-assistant", methods=['POST'])
# def startAdvisorAssistant():
#     request_data = request.json
    
#     requirements_satisfied = request_data["requirements_satisfied"]
#     requirements_not_satisfied = request_data["requirements_not_satisfied"]

#     # TODO - MAKE THIS BASED ON THE TERM
#     with open("fall2025.json", "r") as file:
#         data = json.load(file) 

#     course_matched_data = {}
    
#     # Loop through all the satisfied requirements and find all the course times 
#     for req in requirements_not_satisfied:
#             pattern = r"([A-Z]{2,4}) ((?:\d{4}(?:/\d{4})?,?\s*)+)"

#             # Extract all matches
#             matches = re.findall(pattern, req)

#             courses = []

#             for subject, numbers in matches:
#                 # Find all course numbers, including possible `/` ranges
#                 num_list = re.findall(r"\d{4}(?:/\d{4})?", numbers)
                
#                 for num in num_list:
#                     # If course number contains `/`, split it into two separate entries
#                     if '/' in num:
#                         num1, num2 = num.split('/')
#                         courses.append(f"{subject} {num1}")
#                         courses.append(f"{subject} {num2}")
#                     else:
#                         courses.append(f"{subject} {num}")

#             # Output the final list of parsed courses
#             # print(courses)
            
#             course_matched_data[req] = []
            
#             attr_match = re.search(r'\b[A-Z]{1,2}\d\b', req)
        
#             if attr_match:
#                 attr = attr_match.group(0)
#                 matched_object = find_matching_object(data, attr)
#                 if len(matched_object) > 0:
#                     course_matched_data[req].extend(formatResults(matched_object))

#             for course in courses:
#                 # Find course in JSON

#                 subject = course.split()[0]
#                 course_number = course.split()[1]
                                
#                 matches = [
#                     course for course in data 
#                     if course["subject"] == subject and course["courseNumber"] == course_number
#                 ]
                
#                 # ideal: Find all the prerequisites as well and display that to the user
#                 # might be a lot if the user is a new student, so fetching prerequisites can be done dynamically for an added course
#                 # then it'll check if the pre-requisites are in the list of the course the user has already taken
#                 if len(matches) > 0:
#                     # print(match)
#                     course_matched_data[req].extend(formatResults(matches))
                
    
#     return course_matched_data, 200
    
# def tokenize_prerequisites(raw_texts):
#     """Tokenizes the prerequisites text into meaningful units."""
#     tokens = []
#     course_pattern = re.compile(r"Course or Test:\s*([\w\s\/]+)\s+(\d+)")
#     grade_pattern = re.compile(r"Minimum Grade of ([A-FP])")

#     for text in raw_texts:
#         print(text)
#         print("--0000000---")
        
#         # text = text.replace("\n", " ").strip()  # Flatten text
#         lines = text.split("\n")

#         for line in lines:
#             line = line.strip()

#             if not line:
#                 continue

#             print(line)
#             print("---------")
#             # If the line is just "and" or "or", treat it as a separate token
#             if line.lower() in ("and", "or"):
#                 tokens.append(line.lower())  # Ensure lowercase consistency
#                 continue

    

#         course_match = course_pattern.search(text)
#         grade_match = grade_pattern.search(text)

#         if course_match:
#             subject, course_number = course_match.groups()
#             min_grade = grade_match.group(1) if grade_match else None
#             tokens.append({"subject": subject.strip(), "course_number": course_number, "min_grade": min_grade})

#     return tokens

# def parse_tokens(tokens):
#     """Recursively parses tokens into a nested structure."""
#     stack = []
    
#     while tokens:
#         token = tokens.pop(0)

#         if token == "(":
#             # Start a new group
#             sub_expr = parse_tokens(tokens)
#             stack.append(sub_expr)

#         elif token == ")":
#             # End the current group
#             return stack

#         elif token in ("or", "and"):
#             stack.append(token)

#         else:
#             # Course object
#             stack.append(token)

#     return stack

# def parse_prerequisites(html):
#     """Extracts and structures prerequisite information from HTML."""
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

#     # Tokenize and parse
#     tokens = tokenize_prerequisites(raw_texts)
#     parsed_structure = parse_tokens(tokens)

#     return parsed_structure


# def parse_requirements(html, req_type):
#     """Parses prerequisites or corequisites from HTML using BeautifulSoup."""
#     soup = BeautifulSoup(html, "html.parser")

#     # Find the section based on the req_type (preReqs or coReqs)
#     section = soup.find("section", {"aria-labelledby": req_type})
    
#     if not section:
#         return f"No {req_type} section found."

#     # Check if there is a table (meaning there are requirements)
#     table = section.find("table")
#     if not table:
#         return f"No {req_type.replace('Reqs', ' reqs')} information available."

#     # If it's a prerequisite section
#     if req_type == "preReqs":
#         preq_texts = []
#         for pre in table.find_all("pre"):
#             text = pre.get_text(strip=True).replace("\n", " ")  # Clean formatting
#             preq_texts.append(text)
#         return preq_texts

#     # If it's a corequisite section
#     elif req_type == "coReqs":
#         coreqs = []
#         for row in table.find("tbody").find_all("tr"):
#             cols = row.find_all("td")
#             if len(cols) == 3:
#                 subject, course_number, title = [col.get_text(strip=True) for col in cols]
#                 coreqs.append(f"{subject} {course_number}: {title}")
#         return coreqs
    
# @app.route("/check_course_validity", methods=['POST'])
# def check_course_validity():
#     req = request.json
    
#     requirements_satisfied = req["requirements_satisfied"]
#     course = req["course"]
    
#     # Get course prerequisites 
#     # TODO: Make based on selected term
    
#     # print(course)
#     url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"

#     session = requests.Session()  # Maintain session
#     response = session.get(url)

#     cookies = session.cookies.get_dict()  # Extract cookies

#     # cookies = fetch_cookies("Fall 2025")
#     # cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
     
#     AWSALB = cookies.get("AWSALB", "")
#     AWSALBCORS = cookies.get("AWSALBCORS", "")
#     JSESSIONID = cookies.get("JSESSIONID", "")

#     API_URL_PREREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"
#     API_URL_COREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getCorequisites"

#     # Change term, could access term code from the course itself
#     params = {
#         "term": "202610",
#         "courseReferenceNumber": course['course_reference_number']
#     }
    
#     cookies = {
#             "AWSALB":  AWSALB,
#             "AWSALBCORS": AWSALBCORS,
#             "JSESSIONID":  JSESSIONID,
#     }
    
#     prereqs_response = requests.post(API_URL_PREREQS, params=params, cookies=cookies)
#     coreqs_response = requests.post(API_URL_COREQS, params=params, cookies=cookies)

#     course_prereqs = prereqs_response.text
#     course_coreqs = coreqs_response.text
    
#     prerequisites =  parse_prerequisites(course_prereqs)
#     corequisites = parse_requirements(course_coreqs, "coReqs")
    
#     # print("Prereqs", prerequisites)
#     # print("Coreqs", corequisites)

#     return  jsonify({
#         "prerequisites": prerequisites,
#         "corequisites": corequisites }), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  

