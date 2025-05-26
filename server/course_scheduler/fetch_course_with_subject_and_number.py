from flask import Blueprint, request, jsonify
import json
import os
from pydantic import BaseModel, ValidationError
from  utils.format_course_details import format_course

class RequestDataType(BaseModel):
    subject: str
    course_number: str
    term: str
    
fetch_courses_with_subject_and_number_blueprint = Blueprint('fetch_course_with_subject_and_number', __name__, url_prefix="/api")

@fetch_courses_with_subject_and_number_blueprint.route('/fetch_course_with_subject_and_number', methods=['GET'])
def fetch_course_with_subject_and_number():
    # Validate request
    try:
        request_data = RequestDataType(
            subject=request.args.get('subject'),
            course_number=request.args.get('number'),
            term=request.args.get('term')
        )
    except ValidationError as e:
        if request.args.get('subject') in (None, "") or request.args.get('number') in (None, ""):
            return jsonify({"message": "No subject or course number was passed"}), 400
        
        if request.args.get('term') in (None, ""): 
            return jsonify({"message": "No term was selected"}), 400
        
    # Define term cache file name
    term_name = request_data.term.strip().replace(" ", "").lower()
    term_cache_file = F"{term_name}.json"

    #Open the cache file 
    try:
        with open(os.path.join("cache", term_cache_file), "r") as file:
            courses = json.load(file)
    except FileNotFoundError:
        # Handle when the cache file hasn't been created yet - shouldn't really happen
        print(f"Cache file '{term_cache_file}' not found.")
        
        # TODO: Fetch the course file instead
        return jsonify({
            "message": "There was an error fetching the course cache file. Please run the course viewer on this term and try again"
        })

    # Fetch the course data from the term cache file
    matching_courses = [
        course for course in courses 
        if course.get("subject") == request_data.subject.strip() and
        str(course.get("courseNumber")) == request_data.course_number.strip() and 
        (str(course.get("campusDescription")) == "McNichols Campus" or str(course.get("campusDescription")) == "Online" )
    ]

    processed_courses = []
    
    # Returns all the courses that match
    for course in matching_courses:
        processed_course = format_course(course)
        if(len(processed_course) != 0):
            processed_courses.append(processed_course)
    
    return processed_courses, 200
    