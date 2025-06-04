from flask import Flask, flash, request, redirect, url_for, Blueprint, jsonify
import json
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import os
import requests
from utils.format_course_details import format_course
import re

API_URL_PREREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/courseSearchResults/getPrerequisites"

course_abbrevs = {
        "ACC": "Accounting",
        "ADS": "Addiction Studies",
        "AEV": "Advanced Electric Vehicle",
        "AAS": "African-American Studies",
        "ALCP": "American Language & Culture",
        "ANE": "Anesthesiology",
        "ARB": "Arabic",
        "AENG": "Architectural Engineering",
        "ARCH": "Architecture",
        "BIO": "Biology",
        "BUS": "Business Administration",
        "CCPD": "Career & Prof Development",
        "CAS": "Catholic Studies",
        "CHM": "Chemistry",
        "CHI": "Chinese",
        "CIVE": "Civil Engineering",
        "CST": "Communication Studies",
        "COM": "Community Dentistry",
        "MCD": "Community Development",
        "CSSE": "Comp Sci/Software Engineering",
        "CIS": "Computer & Information Systems",
        "CNS": "Counseling",
        "CJS": "Criminal Justice",
        "CYBE": "Cybersecurity",
        "DATA": "Data Analytics",
        "DENT": "Dental General",
        "ECN": "Economics",
        "ELEE": "Electrical Engineering",
        "ENGR": "Engineering",
        "CTA": "Engineering Co-op",
        "ENL": "English",
        "ETHL": "Ethical Leadership",
        "ETH": "Ethics",
        "FINA": "Fine Arts",
        "FRE": "French",
        "GEO": "Geography",
        "GER": "German",
        "GRA": "Graduate Assistant",
        "HLH": "Health Professions",
        "HSA": "Health Services Administration",
        "HIS": "History",
        "HON": "Honors",
        "INT": "Intelligence Analysis",
        "ISLM": "Islamic Studies",
        "JPN": "Japanese",
        "KOR": "Korean",
        "LAT": "Latin",
        "LAW": "Law",
        "LEAD": "Leadership",
        "LST": "Legal Studies",
        "MLS": "Liberal Studies",
        "MBA": "MBA",
        "MTH": "Mathematics",
        "MENG": "Mechanical Engineering",
        "MUSM": "Museum Studies",
        "MUS": "Music",
        "NUR": "Nursing",
        "PHL": "Philosophy",
        "PAS": "Physician Assistant",
        "PHY": "Physics",
        "PLS": "Polish",
        "POL": "Political Science",
        "MPD": "Product Development",
        "PYC": "Psychology",
        "RELS": "Religious Studies",
        "SCIE": "Science",
        "SWK": "Social Work",
        "SOC": "Sociology",
        "SPA": "Spanish",
        "STA": "Statistics",
        "TRE": "Theatre",
        "UAS": "University Academic Services",
        "VCE": "Vehicle Cyber Engineering",
        "WGS": "Women's & Gender Studies"
    }


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


def parse_prerequisites(html):
    soup = BeautifulSoup(html, 'html.parser')
    prereq_section = soup.find('section', {'aria-labelledby': 'preReqs'})
    if not prereq_section:
        return []

    rows = prereq_section.find_all('tr')
    
    prereqs = []
    current_logic = None  # can be 'and', 'or', or None

    for row in rows:
        td = row.find('td')
        if not td:
            continue

        text = td.get_text(separator=' ', strip=True)

        # Skip headers or meta-info
        if text.startswith("Prerequisites") or text.startswith("General Requirements"):
            continue

        # Detect logic keywords
        logic_match = re.match(r'^\s*(and|or)\b', text, re.IGNORECASE)
        if logic_match:
            current_logic = logic_match.group(1).lower()
            # Strip logic from the rest of the line
            text = re.sub(r'^\s*(and|or)\b', '', text, flags=re.IGNORECASE).strip()

        # Try extracting course name and minimum grade
        course_match = re.search(r'Course or Test:\s*(.*?)\s{2,}', text)
        grade_match = re.search(r'Minimum Grade of\s+([A-F][+-]?)', text)

        if course_match:
            course = course_match.group(1).strip()
            grade = grade_match.group(1).strip() if grade_match else None
            prereqs.append({
                'course': course,
                'min_grade': grade,
                'logic': current_logic
            })
            current_logic = None  # Reset after using it

    return prereqs
    
remove_courses_with_unsatisfied_prereqs_blueprint = Blueprint('remove_courses_with_unsatisfied_prereqs', __name__, url_prefix="/api")

# Takes all the requirements satisfied + those not satisfied , and fetches all the data
@remove_courses_with_unsatisfied_prereqs_blueprint.route('/remove-courses-with-unsatisfied-prereqs', methods=['POST'])
def remove_courses_with_unsatisfied_prereqs():
    
    request_data = request.json

    requirements = request_data['requirements']
    term = request_data["term"]
    term_name = term["description"]
    
    unsatisfied_requirements = requirements["requirements_not_satisfied"]
    
    pattern = re.compile(r'^[A-Z]{3,4} \d{4}$')
    filtered_unsatisfied_requirements = [c for c in unsatisfied_requirements if pattern.match(c)]
        
    print("All Unsatisfied requirements", filtered_unsatisfied_requirements)
    
    # term_name = term_name.strip().replace(" ", "").lower()
    # term_cache_file = F"{term_name}.json"
    
    all_prerequisites = []
    
    courses_with_unsatisfied_prereqs = []
    
    for unsatisfied_course in filtered_unsatisfied_requirements: 
        print('GETTING PREREQS FOR ', unsatisfied_course)
        
        params = {
            "term": term['code'],
            "subjectCode": unsatisfied_course.split()[0],
            "courseNumber": unsatisfied_course.split()[1]
        }
        
        prereqs_response = requests.post(API_URL_PREREQS, params=params)

        prereqs = parse_prerequisites(prereqs_response.text)

        # Gets the small title
        for courses in prereqs:
            course_title = courses['course']
            
            course_subject = ' '.join(course_title.split()[:-1])
            # print(courses)
            
            for abbrev in course_abbrevs:
                # print(abbrev, course_subject, course_abbrevs[abbrev])
                if course_subject == course_abbrevs[abbrev]:
                    new_title = abbrev + ' ' + str(course_title.split()[-1])
                    courses['formatted_course'] = new_title
                 
        print(unsatisfied_course)
        print(prereqs)
        print("\n------------\n")   
        all_prerequisites.extend(prereqs)
        
    
    # print(all_prerequisites)
    
    # Find the course's matching data
    return {}, 200