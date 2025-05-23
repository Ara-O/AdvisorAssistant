from flask import Flask, flash, request, redirect, url_for, Blueprint, jsonify
import json
import uuid
from werkzeug.utils import secure_filename
import os
from pydantic import BaseModel, ValidationError
from utils.format_course_details import format_course
from utils.process_degree_eval_file import process_degree_eval_file

class RequestDataType(BaseModel):
    subject: str
    course_number: str
    term: str
    
upload_degree_evaluation_blueprint = Blueprint('upload_degree_evaluation', __name__, url_prefix="/api")

@upload_degree_evaluation_blueprint.route('/upload_degree_evaluation', methods=['POST'])
def upload_degree_evaluation():
    try:
        print("Uploading degree evaluation file...")
        
        if 'degree_eval' not in request.files:
                return jsonify({"message": "Please upload a file"}), 400
            
        file = request.files['degree_eval']
        
        # Storing file name under unique name
        file_uuid = uuid.uuid4()
        
        file_path = os.path.join("uploads", str(file_uuid))
        
        file.save(file_path)
        
        requirements = process_degree_eval_file(file_path)

        # After processing, delete the file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return requirements, 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "An unexpected error occured"}), 500
        
