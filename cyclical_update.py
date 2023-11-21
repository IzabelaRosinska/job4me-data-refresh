import os

import requests
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
UPDATE_OFFERS = True
SAVE_CHANGES_TO_FILES = False

url = 'https://job4me-recommendation.azurewebsites.net'

headers = {
    'X-API-Key': os.getenv('API_KEY')
}

transformer = SentenceTransformer('sentence-transformers/LaBSE')


def update_embeddings():
    print('Start updating embeddings')
    conn = pyodbc.connect(f'SERVER={server};DATABASE={database};UID={db_username};PWD={db_password};DRIVER={driver}')
    cursor = conn.cursor()

    if UPDATE_EMPLOYEES:
        employees_to_update = get_employers_to_update(cursor)
        print(f'{len(employees_to_update)} employees to update')
        employees_embeddings = get_employees_embeddings(employees_to_update, transformer)
        for employee_id, embeddings in employees_embeddings.items():
            save_employee_embeddings_to_db(cursor, employee_id, embeddings)
            conn.commit()
        if SAVE_CHANGES_TO_FILES:
            update_json('files/employees_embeddings.json', get_json_writable_embeddings(employees_embeddings))
        requests.get(url + '/update_employees_embeddings', headers)

    if UPDATE_OFFERS:
        offers_to_update = get_filtered_offers(cursor, 'actual')
        print(f'{len(offers_to_update)} offers_to update')
        offers_embeddings = get_offers_embeddings(offers_to_update, transformer)
        for offer_id, embeddings in offers_embeddings.items():
            save_offer_embeddings_to_db(cursor, offer_id, embeddings)
            conn.commit()
        if SAVE_CHANGES_TO_FILES:
            update_json('files/offers_embeddings.json', offers_embeddings)
        requests.get(url + '/update_offers_embeddings', headers)

    conn.commit()
    conn.close()
    print('Embeddings updated')


schedule.every(5).minutes.do(update_embeddings)

while True:
    schedule.run_pending()
    time.sleep(1)
