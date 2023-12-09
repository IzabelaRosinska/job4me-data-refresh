import random
from datetime import datetime

import pyodbc
from tqdm import tqdm

from utils.file_reader import read_json
from utils.utils import *


db_username = os.getenv('AZURE_DB_USER')
db_password = os.getenv('AZURE_DB_PASSWORD')
server = os.getenv('AZURE_DB')

database = 'miwm'
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(f'SERVER={server};DATABASE={database};UID={db_username};PWD={db_password};DRIVER={driver}')

cursor = conn.cursor()


def cut(text, char_limit):
    if not text or len(text) < char_limit:
        return text
    while len(text) > char_limit - 1:
        if (index := max(text.rfind("."), text.rfind("\n"), text.rfind(","))) != -1:
            text = text[:index]
        else:
            return ""
    return text + "."


def reset_liked():
    try:
        reset_table('dbo.saved_employees')
    except Exception:
        pass
    try:
        reset_table('dbo.saved_offers')
    except Exception:
        pass
    try:
        reset_table('dbo.saved_employers')
    except Exception:
        pass


def reset_table(table_name, with_id=True):
    cursor.execute(f'DELETE FROM {table_name};')
    if with_id:
        cursor.execute(f"DBCC CHECKIDENT ('{table_name}', RESEED, 0);")


def reset_job_fairs():
    reset_table('dbo.job_fair_employer_participantions')
    reset_table('dbo.job_fairs')


def reset_organizers():
    reset_table('dbo.organizers')


def add_simple_rows(table_name, values):
    for val in values:
        query = f'INSERT INTO {table_name} (name) VALUES (?);'
        cursor.execute(query, val)


def add_all_simple_rows():
    reset_table('dbo.levels')
    add_simple_rows('dbo.levels', levels)
    reset_table('dbo.employment_forms')
    add_simple_rows('dbo.employment_forms', forms)
    reset_table('dbo.contract_types')
    add_simple_rows('dbo.contract_types', contract_types)
    reset_table('dbo.industries')
    add_simple_rows('dbo.industries', industries)
    conn.commit()


def reset_employers():
    reset_table('dbo.employers')


def add_employers():
    companies = read_json('../files/companies.json')
    for name, company in tqdm(companies.items()):
        email = company['contact_email']
        locked = 0
        password = None
        telephone = company['contact_phone']
        role = None
        address = company['address']
        company_name = name
        contact_email = email if random.uniform(0, 1) > 0.8 else None
        description = company['description'] if company['description'] else None
        display_description = description.split('.')[0] if description else 'Najlepsi z najlepszych'
        photo = "https://picsum.photos/100/100"
        query = f'INSERT INTO dbo.employers (email, locked, password, telephone, role, address, company_name, ' \
                f'contact_email, description, display_description, photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); '
        cursor.execute(query, (email, locked, password, telephone, role, address, company_name, contact_email,
                               description, display_description, photo))
    conn.commit()


def add_list_values_to_offer(parent_id, table_name, descriptions, max_char):
    for val in descriptions:
        query = f'INSERT INTO {table_name} (description, job_offer_id) VALUES (?, ?)'
        cursor.execute(query, (cut(val, max_char), parent_id))


def add_connections_to_offer(parent_id, table_name, other_id_name, connected_ids):
    for val in connected_ids:
        print(parent_id, val, table_name)
        query = f'INSERT INTO {table_name} (job_offer_id, {other_id_name}) VALUES (?, ?)'
        cursor.execute(query, (parent_id, val))


def add_list_values_to_employee(parent_id, table_name, descriptions):
    for val in descriptions:
        query = f'INSERT INTO {table_name} (description, employee_id) VALUES (?, ?)'
        cursor.execute(query, (val, parent_id))


def reset_offers():
    reset_table('dbo.job_offer_levels', False)
    reset_table('dbo.job_offer_employment_forms', False)
    reset_table('dbo.job_offer_contract_types', False)
    reset_table('dbo.job_offer_industries', False)
    reset_table('dbo.job_offer_localizations', False)
    reset_table('dbo.localizations')
    reset_table('dbo.extra_skills')
    reset_table('dbo.requirements')
    reset_table('dbo.job_offers')


def add_offers(with_embeddings=False):
    cursor.execute("SELECT IDENT_CURRENT('dbo.job_offers') AS last_inserted_id")
    last_inserted_id = int(row.last_inserted_id) if (row := cursor.fetchone()) else 0

    offers = read_json('../files/offers.json')
    embeddings = read_json('../files/offers_embeddings.json')
    companies = read_json('../files/companies.json')

    cursor.execute('SELECT id, city FROM dbo.localizations;')
    localizations = {city: c_id for c_id, city in cursor.fetchall()}
    cursor.execute("SELECT IDENT_CURRENT('dbo.locations') AS loc_id")
    loc_id = int(row.loc_id) if (row := cursor.fetchone()) and row.loc_id else 0

    i = 0
    companies_dict = {name: str(i := i + 1) for name in companies}
    for j, (offer, offer_embeddings) in tqdm(enumerate(zip(offers.values(), embeddings.values()))):
        if j < 100:
            description = offer['description'] if offer['description'] else None
            duties = offer['duties']
            offer_name = offer['name']
            salary_from = offer['min_salary']
            salary_to = offer['max_salary'] if 'max_salary' in offer else None
            working_time = offer['working_time']
            employer_id = companies_dict[offer['company']]
            if with_embeddings:
                duties_embeddings = np.array(offer_embeddings['duties'], dtype=np.float32).tobytes() \
                    if 'duties' in offer_embeddings else None
                description_embeddings = np.array(offer_embeddings['description'], dtype=np.float32).tobytes() \
                    if 'description' in offer_embeddings else None
                skills_embeddings = np.array(offer_embeddings['requirements+extra_skills'], dtype=np.float32).tobytes() \
                    if 'requirements+extra_skills' in offer_embeddings else None
                query = f'INSERT INTO dbo.job_offers (description, duties, offer_name, salary_from, salary_to, ' \
                        f'working_time, employer_id, duties_embeddings, description_embeddings, skills_embeddings) ' \
                        f'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                cursor.execute(query, (cut(description, 490), cut(duties, 990), offer_name, salary_from, salary_to,
                                       working_time, employer_id, duties_embeddings, description_embeddings,
                                       skills_embeddings))
            else:
                query = f'INSERT INTO dbo.offers (description, duties, offer_name, salary_from, salary_to, working_time, ' \
                        f'employer_id) VALUES (?, ?, ?, ?, ?, ?, ?);'
                cursor.execute(query, (description, duties, offer_name, salary_from, salary_to, working_time, employer_id))
            for localization in offer['localizations']:
                if localization not in localizations:
                    query = f'INSERT INTO dbo.localizations (city) VALUES (?);'
                    cursor.execute(query, localization)
                    loc_id += 1
                    localizations[localization] = loc_id
                add_connections_to_offer(j + last_inserted_id + 1, 'dbo.job_offer_localizations', 'localization_id',
                                         [localizations[localization]])

            add_list_values_to_offer(j + last_inserted_id + 1, 'dbo.extra_skills', offer['extra_skills'], 180)
            add_list_values_to_offer(j + last_inserted_id + 1, 'dbo.requirements', offer['requirements'], 220)
            add_connections_to_offer(j + last_inserted_id + 1, 'dbo.job_offer_levels', 'level_id',
                                     [levels.index(level) + 1 for level in offer['levels']])
            add_connections_to_offer(j + last_inserted_id + 1, 'dbo.job_offer_contract_types', 'contract_type_id',
                                     [contract_types.index(val) + 1 for val in offer['contract_types']])
            add_connections_to_offer(j + last_inserted_id + 1, 'dbo.job_offer_employment_forms',
                                     'employment_form_id', [forms.index(val) + 1 for val in offer['forms']])
            add_connections_to_offer(j + last_inserted_id + 1, 'dbo.job_offer_industries', 'industry_id',
                                     [industries.index(val) + 1 for val in offer['branches']])
            conn.commit()


def reset_employees():
    reset_table('dbo.projects')
    reset_table('dbo.education')

    reset_table('dbo.experience')
    reset_table('dbo.skills')
    reset_table('dbo.employees')


def add_employees():
    employees = read_json('../files/employees.json')

    for i, employee in tqdm(enumerate(employees.values())):
        email = employee['email']
        locked = 0
        password = None
        telephone = employee['phone']
        role = None
        about_me = employee['about_me'] if employee['about_me'] else None
        contact_email = employee['contact_email'] if employee['about_me'] else None
        first_name = employee['name'].split(' ')[0]
        interests = employee['hobbies'] if employee['about_me'] else None
        last_name = employee['name'].split(' ')[1]
        query = f"INSERT INTO dbo.employees (email, locked, password, telephone, role, about_me, contact_email, " \
                f"first_name, interests, last_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?); "
        cursor.execute(query, (email, locked, password, telephone, role, about_me, contact_email, first_name, interests,
                               last_name))
        add_list_values_to_employee(i + 1, 'dbo.education', employee['education'])
        add_list_values_to_employee(i + 1, 'dbo.projects', employee['projects'])
        add_list_values_to_employee(i + 1, 'dbo.experience', employee['work_experience'])
        add_list_values_to_employee(i + 1, 'dbo.skills', employee['skills'])


def add_organizers():
    organizers = read_json('../files/organizers.json')
    for organizer in organizers.values():
        email = organizer['email']
        locked = 0
        password = None
        telephone = organizer['telephone']
        role = None
        description = organizer['description']
        organizer_name = organizer['name']
        contact_email = organizer['contact_email']
        query = f"INSERT INTO dbo.organizers (email, locked, password, telephone, role, description, organizer_name, " \
                f"contact_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?); "
        cursor.execute(query, (email, locked, password, telephone, role, description, organizer_name, contact_email))


def get_employers_dict():
    cursor.execute('SELECT id, company_name FROM dbo.employers')
    rows = cursor.fetchall()
    return {name: employer_id for employer_id, name in rows}


def add_job_fairs():
    job_fairs = read_json('../files/job_fairs.json')
    connections = read_json('../files/job_fairs_employers_connection.json')
    employers_dict = get_employers_dict()

    for job_fair_id, job_fair in job_fairs.items():
        address = job_fair['address']
        data_end = datetime.strptime(job_fair['data_end'], "%Y-%m-%d %H:%M:%S")
        data_start = datetime.strptime(job_fair['data_start'], "%Y-%m-%d %H:%M:%S")
        description = job_fair['description']
        display_description = job_fair['display_description']
        name = job_fair['name']
        photo = "https://picsum.photos/100/100"
        organizer_id = job_fair['organizer']

        query = f"INSERT INTO dbo.job_fairs (address, data_end, data_start, description, display_description, name, " \
                f"photo, organizer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?); "
        cursor.execute(query, (address, data_end, data_start, description, display_description, name, photo,
                               organizer_id))

    for job_fair_id, is_active, employer in connections:
        query = f"INSERT INTO dbo.job_fair_employer_participantions (employer_id, job_fair_id) VALUES (?, ?); "
        cursor.execute(query, (employers_dict[employer], int(job_fair_id)))


def reset_verification_tokens():
    reset_table('dbo.verification_token')


levels = ['Stażysta', 'Junior', 'Mid', 'Senior', "Menedżer"]
forms = ['praca stacjonarna', 'praca hybrydowa', 'praca zdalna']
contract_types = ['umowa o pracę', 'kontrakt B2B', 'umowa zlecenie', 'umowa o staż']
industries = ['IT', 'Sprzedaż', 'Administracja Biura', 'Zdrowie']

reset_liked()
reset_verification_tokens()
reset_job_fairs()
reset_organizers()
reset_employees()
reset_offers()
reset_employers()
add_all_simple_rows()
add_organizers()
add_job_fairs()
add_employers()
add_offers(True)
add_employees()

conn.commit()

conn.close()
