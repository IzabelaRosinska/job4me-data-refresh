import schedule
import time

from db_connection.db_connect import *
from utils.file_reader import *
from process_data import *


server = "tcp:miwmjob4me.database.windows.net,1433"
database = 'miwm'
db_username = "miwm"
db_password = "job4meZPI"
driver = '{ODBC Driver 17 for SQL Server}'


def update_embeddings():
    conn = pyodbc.connect(f'SERVER={server};DATABASE={database};UID={db_username};PWD={db_password};DRIVER={driver}')
    cursor = conn.cursor()
    transformer = SentenceTransformer('sentence-transformers/LaBSE')

    employees_to_update = get_employers_to_update(cursor)
    employees_embeddings = get_employees_embeddings(employees_to_update, transformer)
    for employee_id, embeddings in employees_embeddings.items():
        save_employee_embeddings_to_db(cursor, employee_id, embeddings)
    update_json('files/employees_embeddings.json', employees_embeddings)

    offers_to_update = get_filtered_offers(cursor, 'actual')
    offers_embeddings = get_offers_embeddings(offers_to_update, transformer)
    for offer_id, embeddings in offers_embeddings.items():
        save_offer_embeddings_to_db(cursor, offer_id, embeddings)
    update_json('files/offers_embeddings.json', offers_embeddings)

    conn.commit()
    conn.close()


schedule.every(5).minutes.do(update_embeddings())

while True:
    schedule.run_pending()
    time.sleep(1)
