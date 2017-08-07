from flask import Flask, render_template, redirect
from flask import request
import SurveySender
import DatabaseHelper as db
import logging

app = Flask(__name__)


@app.route('/')
def index():
    return redirect("/create", code=302)


@app.route('/create', methods=['GET'])
def create():
    return render_template('addSurveys.html')


@app.route('/addQuestions/<int:survey_id>', methods=['GET'])
def add_survey_questions(survey_id=0):
    return render_template('addQuestions.html', survey_id=survey_id)


@app.route('/addNumbers/<int:survey_id>', methods=['GET'])
def add_numbers(survey_id=0):
    return render_template('addNumbers.html', survey_id=survey_id)


@app.route('/callback', methods=['POST'])
def parse_request():
    logging.info(request.get_json())
    SurveySender.read_response(request.get_json())
    return ''


@app.route('/api/survey/<int:survey_id>', methods=['GET'])
def get_survey(survey_id):
    return SurveySender.get_survey(survey_id)


@app.route('/api/surveys', methods=['GET', 'POST'])
def create_survey():
    if request.method == 'POST':
        json = request.get_json()
        logging.info(json)
        survey_name = json['surveyName']
        if 'surveyNumber' in json and json['surveyNumber']:
            survey_number = json['surveyNumber']
        else:
            survey_number = SurveySender.create_bandwidth_app()
        survey_id = db.save_survey_to_database(survey_name, survey_number)
        if 'questions' in json:
            SurveySender.parse_questions(json['questions'], survey_id)
        return str(survey_id)
    elif request.method == 'GET':
        return SurveySender.get_all_surveys()
    return None


@app.route('/api/surveys/<int:survey_id>/phoneNumbers', methods=['POST'])
def send_to_numbers(survey_id=0):
    logging.info(request.get_json())
    SurveySender.send_survey_to_numbers(survey_id, request.get_json())
    return "Survey Sent"


@app.route('/api/surveys/<int:survey_id>/questions', methods=['POST'])
def add_questions(survey_id=0):
    logging.info(request.get_json())
    SurveySender.parse_questions(request.get_json(), survey_id)
    return ""


if __name__ == '__main__':
    app.run(debug=True, port=4000)
