import requests
from bs4 import BeautifulSoup
import re
import json

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
# url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"

# session = requests.Session()  # Maintain session
# response = sessi/on.get(url)

API_URL_PREREQS = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/courseSearchResults/getPrerequisites"

# Change term, could access term code from the course itself
# - Don't know if changing the term would matter since the prereqs stay the same
params = {
    "term": "202610",
    "subjectCode": "ACC",
    "courseNumber": "4130"
}
prereqs_response = requests.post(API_URL_PREREQS, params=params)

parsed = parse_prerequisites(prereqs_response.text)

with open("../utils/full_courses.json", 'r') as f:
    course_abbrevs = json.load(f)
    
for courses in parsed:
    course_title = courses['course']
    
    course_subject = ' '.join(course_title.split()[:-1])
    # print(courses)
    
    for abbrev in course_abbrevs:
        # print(abbrev, course_subject, course_abbrevs[abbrev])
        if course_subject == course_abbrevs[abbrev]:
            new_title = abbrev + ' ' + str(course_title.split()[-1])
            courses['formatted_course'] = new_title
            
print(parsed)
    
# coreqs_response = requests.post(API_URL_COREQS, params=params, cookies=cookies)


