from flask import Flask, flash, request, redirect, url_for, Blueprint, jsonify
import json
from werkzeug.utils import secure_filename
import os
from utils.format_course_details import format_course
import re

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
    
start_advisor_assistant_blueprint = Blueprint('start_advisor_assistant', __name__, url_prefix="/api")

@start_advisor_assistant_blueprint.route('/start-advisor-assistant', methods=['POST'])
def start_advisor_assistant():
    request_data = request.json
    term_name = request_data["term_name"]
    term_name = term_name.strip().replace(" ", "").lower()
    term_cache_file = F"{term_name}.json"
    
    requirements_satisfied = request_data["requirements_satisfied"]
    requirements_not_satisfied = request_data["requirements_not_satisfied"]

    with open(os.path.join("cache", term_cache_file), "r") as file:
        data = json.load(file) 

    course_matched_data = {}
    
    # Loop through all the satisfied requirements and find all the course times 
    for req in requirements_not_satisfied:
            pattern = r"([A-Z]{2,4}) ((?:\d{4}(?:/\d{4})?,?\s*)+)"

            # Extract all matches
            matches = re.findall(pattern, req)

            courses = []

            for subject, numbers in matches:
                # Find all course numbers, including possible `/` ranges
                num_list = re.findall(r"\d{4}(?:/\d{4})?", numbers)
                
                for num in num_list:
                    # If course number contains `/`, split it into two separate entries
                    if '/' in num:
                        num1, num2 = num.split('/')
                        courses.append(f"{subject} {num1}")
                        courses.append(f"{subject} {num2}")
                    else:
                        courses.append(f"{subject} {num}")
            
            course_matched_data[req] = []
            
            attr_match = re.search(r'\b[A-Z]{1,2}\d\b', req)
        
            if attr_match:
                attr = attr_match.group(0)
                matched_object = find_matching_object(data, attr)
                if len(matched_object) > 0:
                    for course in matched_object:
                        course_data = format_course(course)
                        
                        if len(course_data) != 0:
                            course_matched_data[req].append(course_data)

            for course in courses:
                # Find course in JSON
                subject = course.split()[0]
                course_number = course.split()[1]
                                
                matches = [
                    course for course in data 
                    if course["subject"] == subject and course["courseNumber"] == course_number
                ]
                
                # ideal: Find all the prerequisites as well and display that to the user
                # might be a lot if the user is a new student, so fetching prerequisites can be done dynamically for an added course
                # then it'll check if the pre-requisites are in the list of the course the user has already taken
                if len(matches) > 0:
                    for course in matches:
                        course_data = format_course(course)
                        
                        if len(course_data) != 0:
                            course_matched_data[req].append(course_data)
                
    
    return course_matched_data, 200