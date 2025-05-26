import os
import json
import requests
from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError, Field
from utils.format_course_details import format_course
from utils.fetch_cookies import fetch_cookies

class RequestDataType(BaseModel):
    term_name: str
    term_code: str
    refresh_course_data: bool = Field(default=False)
    
fetch_courses_blueprint = Blueprint('fetch_courses', __name__, url_prefix="/api")

@fetch_courses_blueprint.route('/fetch_courses', methods=['GET'])
def fetch_courses():
    print("Fetching courses...")
    
    try:
        request_data = RequestDataType(
            term_name=request.args.get('term_name'),
            term_code=request.args.get('term_code'),
            refresh_course_data=request.args.get('refresh_course_data')
        )
    except ValidationError as e:
        if request.args.get('term_name') in (None, "") or request.args.get('term_code') in (None, ""):
            return jsonify({"message": "No term code or term name was passed"}), 400

    term_code = request_data.term_code
    term_name = request_data.term_name
    refresh_course_data = request_data.refresh_course_data
    
    # Format term name
    term_name = term_name.replace(" (View Only)", "")
    max_page_size = 500
    
    # API for fetching the courses
    API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"
    
    term_title = term_name.split(" ")
    term_cache_json_file = "".join(term_title).lower() + ".json"
    
    print(f"Reload the course data/cache: {refresh_course_data}")
   
    # If the user doesn't want to refresh the course data, fetch from cache
    if not refresh_course_data:
        try:
            with open(os.path.join("cache", term_cache_json_file), "r") as file:
                course_data = json.load(file)
                
                courses = []
                
                for course in course_data:
                    formatted_course = format_course(course)
                    
                    if formatted_course:
                        courses.append(formatted_course)
                
                print("Courses fetched successfully from cache")
                return courses, 200

        except FileNotFoundError:
            print('No cache file exists... Generating cache file')
            
    cookies = fetch_cookies(term_name=term_name)
    
    if not cookies:
        print("There was an error fetching the cookies")
        return [], 400
    
    print("Cookies have been fetched...")
        
    cookies_parsed = {cookie["name"]: cookie["value"] for cookie in cookies}
    
    AWSALB = cookies_parsed.get("AWSALB", "")
    AWSALBCORS = cookies_parsed.get("AWSALBCORS", "")
    JSESSIONID = cookies_parsed.get("JSESSIONID", "")
    
    cookies = {
        "AWSALB":  AWSALB,
        "AWSALBCORS": AWSALBCORS,
        "JSESSIONID":  JSESSIONID,
    }

    params = {
        "txt_term": term_code,
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
                
        # Fetch total count - will be used to know how many times to fetch while offsetting
        response = requests.get(API_URL, params=params, cookies=cookies)
        
        response_json = response.json()
        
        total_courses = response_json["totalCount"]
        
        print(f"Total courses length: {total_courses}")
               
        # Start fetching the actual courses        
        courses_data = [] 
        
        print("Fetching all courses...")
        
        for i in range((total_courses//max_page_size) + 1):
            params.update({
                'pageOffset': i * max_page_size,
                "pageMaxSize": max_page_size
            })
            
            response = requests.get(API_URL, params=params, cookies=cookies)
            
            response_json = response.json()
            
            courses_data.extend(response_json["data"])
            
        print("Courses have been fetched")      
          
        # After the courses have been fetched, store the course data in the cache file
        with open(os.path.join("cache", term_cache_json_file), "w", encoding="utf-8") as f:
            json.dump(courses_data, f, indent=4)
        
        courses = []
        
        # Format the course to be of proper format
        for course in courses_data:
            formatted_course = format_course(course)
            
            if len(formatted_course) != 0:
                courses.append(formatted_course)

        return courses, 200

    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error has occured. Please try again later"}), 500
