import sqlite3
import os.path
from datetime import datetime


def get_connection():
    """Get a connection to the database and return the connection and a cursor."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "surveys.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    return connection, cursor


def save_response(response, phone_number, question_id):
    """Save a response to a survey question to the database.

    :param response: The text of the response
    :param phone_number: The phone number the response was sent from
    :param question_id: The question being responded to
    """
    connection, cursor = get_connection()
    cursor.execute(
        'create table if not exists responses ('
        'answer_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'question_id INTEGER, '
        'phone_number nvarchar(15) NOT NULL, '
        'response nvarchar(2000) NOT NULL, '
        'timestamp DATETIME)')
    values = (question_id, phone_number, response, datetime.now())
    cursor.execute('insert into responses(question_id, phone_number, response, timestamp) values(?,?,?,?)', values)
    connection.commit()
    connection.close()


def save_questions(survey_id, questions):
    """Save questions to the database. If a question with the same survey id and index exists, the question is replaced.

    :param survey_id: The survey that the question belongs to
    :param questions: A JSON object representing the questions to add
    """
    connection, cursor = get_connection()
    cursor.execute(
        'create table if not exists questions('
        'question_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'survey_id INTEGER, '
        'question_index INTEGER, '
        'question_text nvarchar(200) NOT NULL)')
    for q in questions:
        if get_question_by_index(survey_id, q['questionIndex']):
            cursor.execute('DELETE FROM questions WHERE survey_id=? AND question_index=?', (survey_id, q['questionIndex']))
        cursor.execute('insert into questions(survey_id, question_index, question_text) values(?,?,?)',
                       (survey_id, q['questionIndex'], q['questionText']))
    connection.commit()
    connection.close()


def save_survey(survey_name, survey_number):
    """Save a survey to the database.

    :param survey_name: The name of the survey
    :param survey_number: The phone number associated with the survey
    """
    connection, cursor = get_connection()
    cursor.execute(
        "create table if not exists surveys("
        "survey_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "survey_name varchar(200), "
        "survey_number varchar(15))")
    cursor.execute('insert into surveys(survey_name, survey_number) values(?,?)', (survey_name, survey_number))
    survey_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return survey_id


def save_status(phone, question_id, send_phone):
    """If the user does not have a current status, save the status to the database.

    :param phone: The phone number of the user taking the survey
    :param question_id: The question the user was most recently sent
    :param send_phone: The phone number for the sender of the survey
    """
    status = get_status(phone, send_phone)
    if status:
        update_status(phone, question_id)
        return
    connection, cursor = get_connection()
    cursor.execute(
        'create table if not exists status('
        'question_id INTEGER, '
        'phone_number nvarchar(15), '
        'send_phone varchar(15))')
    cursor.execute('insert into status(question_id, phone_number, send_phone) values(?,?, ?)',
                   (question_id, phone, send_phone))
    connection.commit()
    connection.close()


def get_question_by_index(survey_id, index):
    """Look up a question in the database based on survey id and index.

    :param survey_id: The survey that the question belongs to
    :param index: The index of the desired question
    :return: The desired question, or None if the question does not exist
    """
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM questions WHERE survey_id=? AND question_index=?",
                   (survey_id, index))
    questions = cursor.fetchall()
    connection.close()
    if not questions:
        return None
    return questions[0]


def get_all_questions(survey_id):
    """Return all questions for a given survey."""
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM questions WHERE survey_id=?", (survey_id,))
    questions = cursor.fetchall()
    connection.close()
    return questions


def get_question_by_id(question_id):
    """Return a question with a given id."""
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM questions WHERE question_id=?", (question_id,))
    question = cursor.fetchall()
    connection.close()
    return question[0]


def get_survey(survey_id):
    """Return a survey with the given id."""
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM surveys WHERE survey_id=?", (survey_id,))
        surveys = cursor.fetchall()
    except sqlite3.OperationalError:
        connection.close()
        return []
    connection.close()
    return surveys[0]


def get_survey_id_by_number(survey_number):
    """Return a survey id based on a survey phone number

    :param survey_number: The phone number associated with the desired survey
    :return: The id of the desired survey
    """
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM surveys WHERE survey_number=?", (survey_number,))
    surveys = cursor.fetchall()
    connection.close()
    return surveys[0][0]


def get_all_surveys():
    """Return all surveys in the database."""
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM surveys")
        surveys = cursor.fetchall()
    except sqlite3.OperationalError:
        surveys = []
    connection.close()
    return surveys


def get_survey_phone_number(survey_id):
    """Return the phone number associated with the desired survey.

    :param survey_id: The id of the desired survey
    :return: The phone number for the desired survey, or an empty list if there is an error
    """
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM surveys WHERE survey_id=?", (survey_id,))
        surveys = cursor.fetchall()
    except sqlite3.OperationalError:
        connection.close()
        return []
    connection.close()
    return surveys[0][2]


def get_responses_by_id(question_id):
    """Return all responses to a question

    :param question_id: The id of the desired question
    :return: A list of responses, or an empty list if there are no responses
    """
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM responses WHERE question_id=?", (question_id,))
        responses = cursor.fetchall()
    except sqlite3.OperationalError:
        responses = []
    connection.close()
    return responses


def get_status(phone_number, send_phone):
    """Return a user's status based on phone numbers.

    :param phone_number: The phone number of the user taking the survey
    :param send_phone: The phone number of the survey the user is taking
    :return: The user's status, or an empty list if the user has no current status for the given survey
    """
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM status WHERE phone_number=? AND send_phone=?", (phone_number, send_phone))
        status = cursor.fetchall()
    except sqlite3.OperationalError:
        return []
    if not status:
        return []
    connection.close()
    return status[0]


def delete_status(phone):
    """Delete the status for a given phone number."""
    connection, cursor = get_connection()
    cursor.execute('DELETE FROM status WHERE phone_number=?', (phone,))
    connection.commit()
    connection.close()


def update_status(phone, question_id):
    """Update the status for a user with a new question id."""
    connection, cursor = get_connection()
    cursor.execute('UPDATE status SET question_id=? WHERE phone_number=(?)', (question_id, phone))
    connection.commit()
    connection.close()
