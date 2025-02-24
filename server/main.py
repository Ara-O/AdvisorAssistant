from flask import Flask, request, jsonify
import requests
import json
import time

app = Flask(__name__)

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
    term = request.args.get("term")
    page_size = 10
    max_page_size = 500
    
    API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"
    # session = requests.Session()
        
    # response = session.get("https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/registration")
        
    # jsession_id = session.cookies.get("JSESSIONID")
    # aws_lab = session.cookies.get("AWSALB")
    # awsalbcors = session.cookies.get("AWSALBCORS")

    # print("JSESSIONID:", jsession_id)
    # print('AWSLAB: ', aws_lab)
    # print("CORS:", awsalbcors)
        
    cookies = {
            "AWSLAB": request.args.get("awslab"),
            "AWSALBCORS": request.args.get("awsalbcors"),
            "JSESSIONID":  request.args.get("jsessionid"),
            # "taxitag_main": "v_id:0193db54b63500803a61c3340d7805046005b00900bd0$_sn:26$_se:3$_ss:0$_st:1740268426041$dc_visit:26$ses_id:1740266596186%3Bexp-session$_pn:3%3Bexp-session$dc_event:3%3Bexp-session$tag_session_91:1%3Bexp-session"
    }
    
    params = {
        "txt_term": str(term),
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
    app.run(host='0.0.0.0', port=10000, debug=True)  

