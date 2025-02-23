from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)


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
    print(term)
    API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/courseSearchResults/courseSearchResults"
    
    session_id = f"6sfui{int(time.time() * 1000)}"
    
    try:
        # Forward the request to the actual API
        response = requests.get(API_URL, params={
            "txt_term": "202610",
            "startDatepicker": "",
            "endDatepicker": "",
            "uniqueSessionId": "6sfui1740316474168",  # Generate a new session ID
            "pageOffset": 3,
            "pageMaxSize": 500,
            "sortColumn": "subjectDescription",
            "sortDirection": "asc",
            "enrollmentDisplaySettings": ""
        }, cookies={
            "AWSLAB": "1U/twyFpZK4hu2uSVLm+TCJx1s3ONXzdV4oTAVcUkmY/sWGeI100u7QJ0QVkAlAKJhw4mOx9BEWsykGaHN5+PW2X3+ct+I+Q0fSjJ1I9gWDXLllB1oEJJv5ONyj/; Expires=Sun, 02 Mar 2025 14:37:58 GMT; Path=/",
            "AWSALBCORS": "1U/twyFpZK4hu2uSVLm+TCJx1s3ONXzdV4oTAVcUkmY/sWGeI100u7QJ0QVkAlAKJhw4mOx9BEWsykGaHN5+PW2X3+ct+I+Q0fSjJ1I9gWDXLllB1oEJJv5ONyj/; Expires=Sun, 02 Mar 2025 14:37:58 GMT; Path=/; SameSite=None; Secure",
            "JSESSIONID": "43D12E9A1F8C7AD8A8E41BE15AD21DAF",
            # "taxitag_main": "v_id:0193db54b63500803a61c3340d7805046005b00900bd0$_sn:26$_se:3$_ss:0$_st:1740268426041$dc_visit:26$ses_id:1740266596186%3Bexp-session$_pn:3%3Bexp-session$dc_event:3%3Bexp-session$tag_session_91:1%3Bexp-session"
        })
        
                
        # Return the API response as JSON
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        print(e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  

