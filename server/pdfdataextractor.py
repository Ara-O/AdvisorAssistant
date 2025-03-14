import base64
from email import message_from_binary_file
from bs4 import BeautifulSoup
# from sql_client import find_element
import json
import ast
import html
from flask import jsonify
import re 


def get_content(cell,index):
    cell_content = cell.decode_contents()
   
    if index == 0:
        if "Yes" in cell_content: return "Yes" 
        return "No"

    cell_soup = BeautifulSoup(cell_content, 'lxml')
    remaining_text = cell_soup.div.next_sibling

    return remaining_text.strip()

# def extract_courses(courses):
#     i = 0
#     courses = courses.strip()
#     courses_list = []
#     while i < len(courses)-3:
#         sub_string = courses[i]+courses[i+1]+courses[i+2]
       
#         if  sub_string.isupper() and sub_string.isalpha():

#             if i+3 < len(courses)-1:
#                 next_char = courses[i+3]
#                 if next_char.isupper() and next_char.isalpha():
#                     sub_string += next_char
#                     i += 1
#             i += 3      
#             u = i - 1


#             while u < len(courses) - 3:
#                 window = courses[u]+courses[u+1]+courses[u+2]+courses[u+3]
#                 sub_window = courses[u] + courses[u+1] + courses[u+2]

             
#                 if sub_window.isalpha() and sub_window.isupper():
#                     i -= 2
#                     break
                    
#                 if window.isdigit():
#                     course_name = sub_string +" "+ window
#                     course_row = find_element(course_name)
#                     courses_list.append({"name":course_name,"details":course_row})
#                 u += 1
#                 i += 1

#         i += 1
#     return courses_list

def find_if_course_has_been_done(token,pre_req):
    for course in token:
        if course["course"] == pre_req[0]:
            return True
    return False

def process_logical_operations(lst):
    # First, handle all 'or' operations
    i = 0
    while i < len(lst):
        if lst[i] == 'or':
            # Replace "False or False" with the result: False
            result = lst[i-1] or lst[i+1]
            # Replace this triplet with the result
            lst = lst[:i-1] + [result] + lst[i+2:]
            i -= 1  # Step back to adjust for the shortened list
        else:
            i += 1

    # Then, handle all 'and' operations
    i = 0
    while i < len(lst):
        if lst[i] == 'and':
            # Replace "True and False" with the result: False
            result = lst[i-1] and lst[i+1]
            # Replace this triplet with the result
            lst = lst[:i-1] + [result] + lst[i+2:]
            i -= 1  # Step back to adjust for the shortened list
        else:
            i += 1

    return lst[0] if lst else False  # Return the single boolean result



def check_if_pre_req_met(token,course):
    if( course == "None") : return False
    if( len(course) == 0) : return False


    pre_req = ast.literal_eval(course[3])
 
    print(pre_req)
    if pre_req == None:   # Case 1 : no pre-req

        return True
    
    if len(pre_req) == 1:
        pre_req = pre_req[0].split(",")  

        if find_if_course_has_been_done(token, pre_req):
  
            return True
        else:

            return False
    
    for i in range(len(pre_req)):
        element = pre_req[i]
        if element == "or" or element == "and":
            continue
        pre_req_details = pre_req[i].split(",")
        pre_req[i] = find_if_course_has_been_done(token, pre_req_details)

    met = (process_logical_operations(pre_req))

    if met:

        return True
    else:
    
        return False 
    

def create_student_plan(token,needed):
    complete_plan = ""    
    for courses in needed:
        plan = ""
        for element in courses: 
            course = find_element(element)
            if len(course) > 0:
                if check_if_pre_req_met(token,course):
                    plan += element +" : "+ course[0][2] + ", "+course[0][4]
                    plan += " or "
        if plan != "":
            complete_plan += plan +"\n"
        plan = ""
    print("******************************")
    print("******************************")
    print("Student plan for winter 2024: ")
    print(complete_plan)
    
def clean_attribute(attr_value):
    if attr_value:
        decoded = html.unescape(attr_value)  # Convert &quot; → "
        decoded = re.sub(r'3D"', '', decoded)  # Remove "3D"
        return decoded.strip()
    return ""


def clean_text(text):
    text = re.sub(r'=\s*', '', text)

    # Fix missing spaces between words by adding a space before capital letters if needed
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between lowercase-uppercase transitions

    # Restore spaces that may have been lost before hyphens
    text = re.sub(r'(?<=\w)-(?=\w)', ' - ', text)  # Ensure spaces around hyphens

    # Remove non-breaking spaces and weird encoded characters
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')

    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)
            
    text = text.replace('COMP', '')
            
    text = text.replace("Area Name:20 ", "")
    
    text = text.strip()
    
    text = text.replace("Requirement ", "")
    
    return text 

def process_student_profile(file):
    mhtml_file = file

    # Step 1: Read and parse the MHTML file
    with open(mhtml_file, 'rb') as file:
        msg = message_from_binary_file(file)
        
    # Step 2: Find and decode the HTML part
    html_part = None
    
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_part = part.get_payload(decode=True)
            break

    if html_part is None:
        print("No HTML part found in the MHTML file.")
        return jsonify({"message": "There was no HTML found"}), 400
    
    # Decode HTML content if it is base64-encoded
    try:
        html_content = base64.b64decode(html_part).decode('utf-8')
     
    except:
        html_content = html_part.decode('utf-8')
    
    # Step 3: Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html')
    tables = soup.find_all('table')
    
    areas = []
    
    for i in range(len(tables)):
        table = tables[i]
        new_area={}
        caption = table.find('caption')
            
        if caption is not None:
            new_area["caption"] = clean_text(caption.text)
            
            requirements_unsafisfied = table.select('[color="#EE0000"]')
            
            new_area["courses"] = []
            
            # For all the unsatisfied requirements in an area, append it under its associated courses
            for req in requirements_unsafisfied:
                row = req.parent.parent
                tds = row.find_all("td")
                courses = tds[1].text
                text = clean_text(courses)
                new_area["courses"].append(text)
            
            if len(requirements_unsafisfied) > 0 and new_area["caption"] != "Program Description" and new_area["caption"] != "Program Evaluation":
                areas.append(new_area)
    
    requirements_satisfied_elements =  soup.select('[color="#000000"]')
    requirements_satisfied = []

    for req in requirements_satisfied_elements:
        row = req.parent.parent
        
        print(row)
        print("\n\n")
        tds = row.find_all("td")
        if len(tds)>7:
            course = tds[3].text.replace("Satisfied By","").replace("\xa0"," ")
            grade = tds[7].text.replace("Grade","").replace("\n","")
            # print(course, tds[3])
            subject = course.split(" ")
            if(len(subject)<2): 
                continue
            
            subject_num = subject[1]
            subject = subject[0]

            subjects_map = json.load(open("full_courses.json","r"))

            subject_description = subject
            
            if subject in subjects_map:
                subject_description = subjects_map[subject]
            
            course = subject + " " + subject_num

            requirements_satisfied.append({
                "course":course,
                "grade":grade
            })

    return {
        "requirements_satisfied":  requirements_satisfied,
        "requirements_not_satisfied": areas   
    }
    




