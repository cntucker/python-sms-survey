import bandwidth
import DatabaseHelper as db
import json
from bandwidth import account

APPLICATION_NAME = 'Survey Application'
BANDWIDTH_USER_ID = '***REMOVED***'
BANDWIDTH_API_TOKEN = '***REMOVED***'
BANDWIDTH_API_SECRET = '***REMOVED***'
CALLBACK_URL = '***REMOVED***'
PREFERRED_AREA_CODE = '336'



def init_bandwidth_account_client():
    """Initialize a Bandwidth account client."""
    account_api = account.Client(BANDWIDTH_USER_ID, BANDWIDTH_API_TOKEN,
                                 BANDWIDTH_API_SECRET)
    return account_api


def init_bandwidth_messaging_client():
    """Initialize a Bandwidth messaging client."""
    messaging_api = bandwidth.client('messaging', BANDWIDTH_USER_ID, BANDWIDTH_API_TOKEN,
                                     BANDWIDTH_API_SECRET)
    return messaging_api


def get_bandwidth_phone_number(account_api, app_id):
    """Order a new phone number and add it to the application."""
    numbers = account_api.search_and_order_local_numbers(area_code=PREFERRED_AREA_CODE, quantity=1)
    my_number = numbers[0]['number']
    account_api.update_phone_number(my_number, application_id=app_id)
    return my_number


def create_bandwidth_app():
    """Search applications to check if any match the given callback url. If there are no matches, create a new application."""
    account_api = init_bandwidth_account_client()
    apps = account_api.list_applications()
    for app in apps:
        if app['incoming_sms_url'] == CALLBACK_URL and app['callback_http_method'] == 'post':
            return get_bandwidth_phone_number(account_api, app['id'])
    app_id = account_api.create_application(name=APPLICATION_NAME, incoming_message_url=CALLBACK_URL,
                                            callback_http_method="POST")
    return get_bandwidth_phone_number(account_api, app_id)


def send_next_question(rec_phone, send_phone, question):
    """Send the next survey question.

    :param rec_phone: The phone number that will be receiving the question
    :param send_phone: The phone number associated with the survey
    :param question: The question text to be sent
    """
    messaging_api = init_bandwidth_messaging_client()
    messaging_api.send_message(from_=send_phone, to=rec_phone, text=question[3])
    db.save_status(phone=rec_phone, question_id=question[0], send_phone=send_phone)


def start_survey(user_number, survey_number):
    """Get the first question for a given survey and begin the survey.

    :param user_number: The number that will be receiving the survey
    :param survey_number: The number associated with the survey
    """
    survey_id = db.get_survey_id_by_number(survey_number)
    first_question = db.get_question_by_index(survey_id, 0)
    send_next_question(user_number, survey_number, first_question)


def read_response(response):
    """If the user has not been given a survey, send the first question. Otherwise, save the response and
    send the next survey question. If there are no additional questions, remove the user's status.

    :param response: The JSON response received.
    """
    text_response = response["text"]
    phone_number = response["from"]
    send_phone = response["to"]
    status = db.get_status(phone_number, send_phone)
    if not status:
        start_survey(phone_number, send_phone)
        return
    db.save_response(response=text_response, phone_number=phone_number, question_id=status[0])
    question = db.get_question_by_id(status[0])
    next_question = db.get_question_by_index(question[1], question[2] + 1)
    if not next_question:
        db.delete_status(phone_number)
        return
    send_next_question(rec_phone=phone_number, send_phone=response["to"], question=next_question)


def get_survey(survey_id):
    """Return all of the data for a given survey

    :param survey_id: The id of the desired survey
    :return: A JSON object with all survey info, as well as all associated questions and responses
    """
    survey_data = db.get_survey(survey_id)
    if not survey_data:
        return json.dumps({})
    question_list = db.get_all_questions(survey_data[0])
    data = {'surveyId': survey_data[0], 'surveyName': survey_data[1], 'questions': []}
    for question in question_list:
        question_data = {'questionId': question[0], 'questionIndex': question[2], 'questionText': question[3],
                         'answers': []}
        response_list = db.get_responses_by_id(question[0])
        for response in response_list:
            response_data = {'answerId': response[0], 'phoneNumber': response[2], 'answerText': response[3],
                             'timestamp': response[4]}
            question_data['answers'].append(response_data)
        data['questions'].append(question_data)
    json_data = json.dumps(data)

    return json_data


def get_all_surveys():
    """Get all surveys and convert them to a JSON object.

    :return: A JSON object containing a list of all surveys
    """
    surveys = db.get_all_surveys()
    data = {'surveys': []}
    for s in surveys:
        survey_data = {'surveyId': s[0], 'surveyName': s[1], 'surveyNumber': s[2]}
        data['surveys'].append(survey_data)
    json_data = json.dumps(data)
    return json_data


def send_survey_to_numbers(survey_id, numbers):
    """Send a survey to a list of numbers

    :param survey_id: The survey to send
    :param numbers: The list of numbers that will receive the survey
    """
    first_question = db.get_question_by_index(survey_id, 0)
    if not first_question:
        return
    send_number = db.get_survey_phone_number(survey_id)
    for num in numbers:
        send_next_question(num, send_number, first_question)


def create_survey(json):
    """Create a survey from a JSON object. Save questions if any are given.

    :param json: The JSON object containing survey info
    :return: The id of the new survey
    """
    survey_name = json['surveyName']
    if 'surveyNumber' in json and json['surveyNumber']:
        survey_number = json['surveyNumber']
    else:
        survey_number = create_bandwidth_app()
    survey_id = db.save_survey(survey_name, survey_number)
    if 'questions' in json:
        db.save_questions(survey_id=survey_id, questions=json['questions'])
    return str(survey_id)
