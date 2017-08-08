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
        logging.info(request.get_json())
        return SurveySender.create_survey(request.get_json())
    else:
        return SurveySender.get_all_surveys()


@app.route('/api/surveys/<int:survey_id>/phoneNumbers', methods=['POST'])
def send_to_numbers(survey_id=0):
    logging.info(request.get_json())
    SurveySender.send_survey_to_numbers(survey_id, request.get_json())
    return "Survey Sent"


@app.route('/api/surveys/<int:survey_id>/questions', methods=['POST'])
def add_questions(survey_id=0):
    logging.info(request.get_json())
    db.save_questions(survey_id=survey_id, questions=request.get_json())
    return "Questions Added"


if __name__ == '__main__':
    app.run(debug=True, port=4000)
