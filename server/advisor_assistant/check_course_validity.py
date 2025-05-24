from flask import Flask, flash, request, redirect, url_for, Blueprint, jsonify
from werkzeug.utils import secure_filename
from pydantic import BaseModel, ValidationError
from utils.format_course_details import format_course
from utils.process_degree_eval_file import process_degree_eval_file
import requests
from bs4 import BeautifulSoup
import re

def tokenize_prerequisites(raw_texts):
    """Tokenizes the prerequisites text into meaningful units."""
    tokens = []
    course_pattern = re.compile(r"Course or Test:\s*([\w\s\/]+)\s+(\d+)")
    grade_pattern = re.compile(r"Minimum Grade of ([A-FP])")

    for text in raw_texts:
        print(text)
        print("--0000000---")
        
        # text = text.replace("\n", " ").strip()  # Flatten text
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # If the line is just "and" or "or", treat it as a separate token
            if line.lower() in ("and", "or"):
                tokens.append(line.lower())  # Ensure lowercase consistency
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
    
    
check_course_validity_blueprint = Blueprint('check_course_validity', __name__, url_prefix="/api")

@check_course_validity_blueprint.route('/check-course-validity', methods=['POST'])
def check_course_validity():
    req = request.json
    requirements_satisfied = req["requirements_satisfied"]
    course = req["course"]
  
    url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"

    session = requests.Session()  # Maintain session
    response = session.get(url)

    cookies = session.cookies.get_dict()  # Extract cookies

    AWSALB = cookies.get("AWSALB", "")
    AWSALBCORS = cookies.get("AWSALBCORS", "")
    JSESSIONID = cookies.get("JSESSIONID", "")

    API_URL_PREREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"
    API_URL_COREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getCorequisites"

    # Change term, could access term code from the course itself
    # - Don't know if changing the term would matter since the prereqs stay the same
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
    
    # print("Prereqs", prerequisites)
    # print("Coreqs", corequisites)

    return  jsonify({
        "prerequisites": prerequisites,
        "corequisites": corequisites }), 200