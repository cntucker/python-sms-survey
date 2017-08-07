import sqlite3
import os.path
from datetime import datetime


def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "surveys.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    return connection, cursor


def save_response_to_database(response, phone_number, question_id):
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


def save_questions_to_database(survey_id, questions):
    connection, cursor = get_connection()
    cursor.execute(
        'create table if not exists questions('
        'question_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'survey_id INTEGER, '
        'question_index INTEGER, '
        'question_text nvarchar(200) NOT NULL)')
    count = 0
    for q in questions:
        if get_questions_from_database(survey_id, q[1]):
            cursor.execute('DELETE FROM questions WHERE survey_id=? AND question_index=?', (survey_id, q[1]))
        cursor.execute('insert into questions(survey_id, question_index, question_text) values(?,?,?)',
                       (survey_id, q[1], q[0]))
        question_id = cursor.lastrowid
        questions[count] = (q, question_id)
        count += 1
    connection.commit()
    connection.close()
    return questions


def save_survey_to_database(survey_name, survey_number):
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


def save_status_to_database(phone, question_id, send_phone):
    status = get_status_from_database(phone, send_phone)
    if status:
        update_status_in_database(phone, question_id)
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


def get_questions_from_database(survey_id, index):
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM questions WHERE survey_id=? AND question_index=?  ORDER BY question_id DESC",
                   (survey_id, index))
    questions = cursor.fetchall()
    connection.close()
    if not questions:
        return None
    return questions[0]


def get_all_survey_questions(survey_id):
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM questions WHERE survey_id=?", (survey_id,))
    questions = cursor.fetchall()
    connection.close()
    return questions


def get_questions_from_database_by_id(question_id):
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM questions WHERE question_id=?", (question_id,))
    question = cursor.fetchall()
    connection.close()
    return question[0]


def get_survey_from_database(survey_id):
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
    connection, cursor = get_connection()
    cursor.execute("SELECT * FROM surveys WHERE survey_number=?", (survey_number,))
    surveys = cursor.fetchall()
    connection.close()
    return surveys[0][0]


def get_all_surveys_from_database():
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM surveys")
        surveys = cursor.fetchall()
    except sqlite3.OperationalError:
        surveys = []
    connection.close()
    return surveys


def get_survey_phone_number(survey_id):
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM surveys WHERE survey_id=?", (survey_id,))
        surveys = cursor.fetchall()
    except sqlite3.OperationalError:
        connection.close()
        return []
    connection.close()
    return surveys[0][2]


def get_responses_from_database_by_id(question_id):
    connection, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM responses WHERE question_id=?", (question_id,))
        responses = cursor.fetchall()
    except sqlite3.OperationalError:
        responses = []
    connection.close()
    return responses


def get_status_from_database(phone_number, send_phone):
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


def delete_status_in_database(phone):
    connection, cursor = get_connection()
    cursor.execute('DELETE FROM status WHERE phone_number=?', (phone,))
    connection.commit()
    connection.close()


def update_status_in_database(phone, question_id):
    connection, cursor = get_connection()
    cursor.execute('UPDATE status SET question_id=? WHERE phone_number=(?)', (question_id, phone))
    connection.commit()
    connection.close()
