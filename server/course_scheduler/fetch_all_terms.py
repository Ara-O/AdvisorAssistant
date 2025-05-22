from flask import Blueprint, request, jsonify
import requests
from pydantic import BaseModel, ValidationError
from  utils.format_course_details import format_course

# class RequestDataType(BaseModel):
#     subject: str
#     course_number: str
#     term: str
    
fetch_all_terms_blueprint = Blueprint('fetch_all_terms', __name__, url_prefix="/api")


@fetch_all_terms_blueprint.route('/fetch_all_terms', methods=['GET'])
def fetch_all_terms():
    try:
        API_URL = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/getTerms" 
        
        # Forward the request to the terms API
        response = requests.get(API_URL, params={
            "searchTerm": "", 
            "offset": 1, 
            "max": 10, 
        })
        
        # Return the API response as JSON
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        print(e)
        return jsonify({"message": "There was an error retrieving the terms"}), 500