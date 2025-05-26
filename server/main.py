import os
from flask import Flask, request
import requests
from flask_cors import CORS
from dotenv import load_dotenv
from course_scheduler.fetch_course_with_subject_and_number import fetch_courses_with_subject_and_number_blueprint
from course_scheduler.fetch_all_terms import fetch_all_terms_blueprint
from course_scheduler.fetch_courses import fetch_courses_blueprint
from advisor_assistant.upload_degree_evaluation import upload_degree_evaluation_blueprint
from advisor_assistant.check_course_validity import check_course_validity_blueprint
from advisor_assistant.start_advisor_assistant import start_advisor_assistant_blueprint

# Load the variables in the .env file
load_dotenv()

app = Flask(__name__)

CORS(app=app)

app.register_blueprint(fetch_courses_with_subject_and_number_blueprint)
app.register_blueprint(fetch_all_terms_blueprint)
app.register_blueprint(fetch_courses_blueprint)
app.register_blueprint(upload_degree_evaluation_blueprint)
app.register_blueprint(start_advisor_assistant_blueprint)
app.register_blueprint(check_course_validity_blueprint)

@app.route('/health', methods=['GET'])
def health():
    return "The app is running!"

MAILGUN_API_URL = os.getenv("MAILGUN_API_URL")
api_key = os.getenv("MAILGUN_API_KEY")

@app.route("/send_feedback", methods=['POST'])
def send_feedback():
    try:
        feedback_message = request.json["feedback_message"]
        print(feedback_message)
        
        resp = requests.post(MAILGUN_API_URL, auth=("api", api_key),
                             data={"from": "oladipoeyiara@gmail.com",
                                   "to": "oladipoeyiara@gmail.com", "subject": "Course Viewer Feedback", "text": feedback_message})
        
        print(resp)
        return "Feedback sent successfully", 200
    except Exception as ex: 
        print(ex)
        return "Error", 500


    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  

