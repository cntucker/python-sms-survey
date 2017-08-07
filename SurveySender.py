import bandwidth
import DatabaseHelper as db
import json
from bandwidth import account

BANDWIDTH_USER_ID = '<User ID>'
BANDWIDTH_API_TOKEN = '<Token>'
BANDWIDTH_API_SECRET = '<Secret>'
CALLBACK_URL = '<Callback URL>'
PREFERRED_AREA_CODE = '<3 Digit Area Code>'


def init_bandwidth_account_client():
    account_api = account.Client(BANDWIDTH_USER_ID, BANDWIDTH_API_TOKEN,
                                 BANDWIDTH_API_SECRET)
    return account_api


def init_bandwidth_messaging_client():
    messaging_api = bandwidth.client('messaging', BANDWIDTH_USER_ID, BANDWIDTH_API_TOKEN,
                                     BANDWIDTH_API_SECRET)
    return messaging_api


def get_bandwidth_phone_number(account_api, app_id):
    numbers = account_api.search_and_order_local_numbers(area_code=PREFERRED_AREA_CODE, quantity=1)
    my_number = numbers[0]['number']
    account_api.update_phone_number(my_number, application_id=app_id)
    return my_number


def create_bandwidth_app():
    account_api = init_bandwidth_account_client()
    apps = account_api.list_applications()
    for app in apps:
        if app['incoming_sms_url'] == CALLBACK_URL and app['callback_http_method'] == 'post':
            return get_bandwidth_phone_number(account_api, app['id'])
    app_id = account_api.create_application(name="Survey Application", incoming_message_url=CALLBACK_URL,
                                            callback_http_method="POST")
    return get_bandwidth_phone_number(account_api, app_id)


def send_next_question(rec_phone, send_phone, question):
    messaging_api = init_bandwidth_messaging_client()
    messaging_api.send_message(from_=send_phone, to=rec_phone, text=question[3])
    db.save_status_to_database(phone=rec_phone, question_id=question[0], send_phone=send_phone)


def start_survey(user_number, survey_number):
    survey_id = db.get_survey_id_by_number(survey_number)
    send_next_question(user_number, survey_number, db.get_questions_from_database(survey_id, 0))


def read_response(response):
    text_response = response["text"]
    phone_number = response["from"]
    send_phone = response["to"]
    status = db.get_status_from_database(phone_number, send_phone)
    if not status:
        start_survey(phone_number, send_phone)
        return
    db.save_response_to_database(response=text_response, phone_number=phone_number, question_id=status[0])
    question = db.get_questions_from_database_by_id(status[0])
    next_question = db.get_questions_from_database(question[1], question[2] + 1)
    if not next_question:
        db.delete_status_in_database(phone_number)
        return
    send_next_question(rec_phone=phone_number, send_phone=response["to"], question=next_question)


def get_survey(survey_id):
    survey_data = db.get_survey_from_database(survey_id)
    if not survey_data:
        return json.dumps({})
    question_list = db.get_all_survey_questions(survey_data[0])
    data = {'surveyId': survey_data[0], 'surveyName': survey_data[1], 'questions': []}
    for question in question_list:
        question_data = {'questionId': question[0], 'questionIndex': question[2], 'questionText': question[3],
                         'answers': []}
        response_list = db.get_responses_from_database_by_id(question[0])
        for response in response_list:
            response_data = {'answerId': response[0], 'phoneNumber': response[2], 'answerText': response[3],
                             'timestamp': response[4]}
            question_data['answers'].append(response_data)
        data['questions'].append(question_data)
    json_data = json.dumps(data)

    return json_data


def parse_questions(questions, survey_id):
    question_list = []
    for q in questions:
        question_list.append((q['questionText'], q['questionIndex']))
    db.save_questions_to_database(survey_id, question_list)


def get_all_surveys():
    surveys = db.get_all_surveys_from_database()
    data = {'surveys': []}
    for s in surveys:
        survey_data = {'surveyId': s[0], 'surveyName': s[1], 'surveyNumber': s[2]}
        data['surveys'].append(survey_data)
    json_data = json.dumps(data)
    return json_data


def send_survey_to_numbers(survey_id, numbers):
    first_question = db.get_questions_from_database(survey_id, 0)
    if not first_question:
        return
    send_number = db.get_survey_phone_number(survey_id)
    for num in numbers:
        send_next_question(num, send_number, first_question)
