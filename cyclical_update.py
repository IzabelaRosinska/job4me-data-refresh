import os

import schedule
import time

from db_connection.db_connect import *
from utils.file_reader import *
from process_data import *
from utils.utils import get_json_writable_embeddings


server = os.getenv('AZURE_DB')
database = 'miwm'
db_username = os.getenv('AZURE_DB_USER')
db_password = os.getenv('AZURE_DB_PASSWORD')
driver = '{ODBC Driver 17 for SQL Server}'

UPDATE_EMPLOYEES = True
UPDATE_OFFERS = False
SAVE_CHANGES_TO_FILES = False


def update_embeddings():
    print('Start updating embeddings')
    conn = pyodbc.connect(f'SERVER={server};DATABASE={database};UID={db_username};PWD={db_password};DRIVER={driver}')
    cursor = conn.cursor()
    transformer = SentenceTransformer('sentence-transformers/LaBSE')

    if UPDATE_EMPLOYEES:
        employees_to_update = get_employers_to_update(cursor)
        print(f'{len(employees_to_update)} employees to update')
        employees_embeddings = get_employees_embeddings(employees_to_update, transformer)
        for employee_id, embeddings in employees_embeddings.items():
            save_employee_embeddings_to_db(cursor, employee_id, embeddings)
            conn.commit()
        if SAVE_CHANGES_TO_FILES:
            update_json('files/employees_embeddings.json', get_json_writable_embeddings(employees_embeddings))

    if UPDATE_OFFERS:
        offers_to_update = get_filtered_offers(cursor, 'actual')
        print(f'{len(offers_to_update)} offers_to update')
        offers_embeddings = get_offers_embeddings(offers_to_update, transformer)
        for offer_id, embeddings in offers_embeddings.items():
            save_offer_embeddings_to_db(cursor, offer_id, embeddings)
            conn.commit()
        if SAVE_CHANGES_TO_FILES:
            update_json('files/offers_embeddings.json', offers_embeddings)

    conn.commit()
    conn.close()
    print('Embeddings updated')


schedule.every(1).seconds.do(update_embeddings)

while True:
    schedule.run_pending()
    time.sleep(1)
