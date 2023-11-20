import numpy as np
import pyodbc


def put_offer_list_values(cursor, offer, offer_id):
    cursor.execute(f'SELECT description FROM dbo.extra_skills WHERE job_offer_id = {offer_id};')
    offer['extra_skills'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT description FROM dbo.requirements WHERE job_offer_id = {offer_id};')
    offer['requirements'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT name FROM dbo.industries i JOIN dbo.job_offer_industries oi ON oi.industry_id = i.id WHERE '
                   f'oi.job_offer_id = {offer_id};')
    offer['branches'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT level_id FROM dbo.job_offer_levels WHERE job_offer_id = {offer_id};')
    offer['levels'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT contract_type_id FROM dbo.job_offer_contract_types WHERE job_offer_id = {offer_id};')
    offer['contract_types'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT employment_form_id FROM dbo.job_offer_employment_forms WHERE job_offer_id = {offer_id};')
    offer['forms'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT localization_id FROM dbo.job_offer_localizations WHERE job_offer_id = {offer_id};')
    offer['localizations'] = [data[0] for data in cursor.fetchall()]


def put_all_offers_list_values(cursor, offers):
    cursor.execute(f'SELECT job_offer_id, description FROM dbo.extra_skills;')
    for row in cursor.fetchall():
        offers[row[0]]['extra_skills'] = row[1]
    cursor.execute(f'SELECT job_offer_id, description FROM dbo.requirements;')
    for row in cursor.fetchall():
        offers[row[0]]['requirements'] = row[1]
    cursor.execute(f'SELECT oi.job_offer_id, i.name FROM dbo.industries i '
                   f'JOIN dbo.job_offer_industries oi ON oi.industry_id = i.id;')
    for row in cursor.fetchall():
        offers[row[0]]['branches'] = row[1]
    cursor.execute(f'SELECT job_offer_id, level_id FROM dbo.job_offer_levels;')
    for row in cursor.fetchall():
        offers[row[0]]['levels'] = row[1]
    cursor.execute(f'SELECT job_offer_id, contract_type_id FROM dbo.job_offer_contract_types;')
    for row in cursor.fetchall():
        offers[row[0]]['contract_types'] = row[1]
    cursor.execute(f'SELECT job_offer_id, employment_form_id FROM dbo.job_offer_employment_forms;')
    for row in cursor.fetchall():
        offers[row[0]]['forms'] = row[1]
    cursor.execute(f'SELECT job_offer_id, localization_id FROM dbo.job_offer_localizations;')
    for row in cursor.fetchall():
        offers[row[0]]['localizations'] = row[1]


def get_offer_by_id(cursor: pyodbc.Cursor, offer_id):
    cursor.execute(f'SELECT offer_name, salary_from, duties, description, duties_embeddings, '
                   f'description_embeddings, skills_embeddings FROM dbo.job_offers WHERE id = {offer_id};')
    row = cursor.fetchone()
    if not row:
        return None
    offer = {'name': row[0], 'min_salary': row[1], 'duties': row[2], 'description': row[3]}
    offer_embeddings = {'duties': np.frombuffer(row[4], dtype=np.float32),
                        'description': np.frombuffer(row[5], dtype=np.float32),
                        'requirements+extra_skills': np.frombuffer(row[6], dtype=np.float32)}
    put_offer_list_values(cursor, offer, offer_id)
    return offer, offer_embeddings


def get_all_offers(cursor: pyodbc.Cursor):
    cursor.execute(f'SELECT id, offer_name, salary_from, duties, description, duties_embeddings, '
                   f'description_embeddings, skills_embeddings FROM dbo.job_offers;')
    rows = cursor.fetchall()
    offers = {}
    offers_embeddings = {}
    for row in rows:
        offers[row[0]] = {'name': row[1], 'min_salary': row[2], 'duties': row[3], 'description': row[4]}
        embeddings = {}
        if row[5]:
            embeddings['duties'] = np.frombuffer(row[5], dtype=np.float32)
        if row[6]:
            embeddings['description'] = np.frombuffer(row[6], dtype=np.float32)
        if row[7]:
            embeddings['requirements+extra_skills'] = np.frombuffer(row[7], dtype=np.float32)
        offers_embeddings[row[0]] = embeddings
    put_all_offers_list_values(cursor, offers)
    return offers, offers_embeddings


def save_offer_embeddings_to_db(cursor, offer_id, embeddings):
    query = f'UPDATE dbo.job_offers SET duties_embeddings = ?, description_embeddings = ?, skills_embeddings = ?, ' \
            f'actual = ? WHERE id = {offer_id}; '
    cursor.execute(query, (bytes(embeddings["duties"]) if "duties" in embeddings else None,
                           bytes(embeddings["description"]) if "description" in embeddings else None,
                           bytes(embeddings["requirements+extra_skills"]) if "requirements+extra_skills" in
                                                                             embeddings else None, 1))


def save_employee_embeddings_to_db(cursor, employee_id, embeddings):
    query = f'UPDATE dbo.employees SET experience_embeddings = ?, skills_embeddings = ?, description_embeddings = ?, ' \
            f'is_embedding_current = ? WHERE id = {employee_id}; '
    cursor.execute(query, (bytes(embeddings["work_experience+projects"]) if "work_experience+projects" in embeddings
                           else None, bytes(embeddings["skills"]) if "skills" in embeddings else None,
                           bytes(embeddings["about_me+hobbies"]) if "about_me+hobbies" in embeddings else None, 1))


def get_employee_by_id(cursor: pyodbc.Cursor, employee_id: int):
    cursor.execute(f'SELECT about_me, interests FROM dbo.employees WHERE id = {employee_id};')
    row = cursor.fetchone()
    if not row:
        return None
    employee = {'about_me': row[0], 'hobbies': row[1]}
    cursor.execute(f'SELECT description FROM dbo.education WHERE employee_id = {employee_id};')
    employee['education'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT description FROM dbo.experience WHERE employee_id = {employee_id};')
    employee['experience'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT description FROM dbo.projects WHERE employee_id = {employee_id};')
    employee['projects'] = [data[0] for data in cursor.fetchall()]
    cursor.execute(f'SELECT description FROM dbo.skills WHERE employee_id = {employee_id};')
    employee['skills'] = [data[0] for data in cursor.fetchall()]
    return employee


def get_all_employees(cursor: pyodbc.Cursor):
    cursor.execute(f'SELECT id, about_me, interests, experience_embeddings, skills_embeddings, description_embeddings '
                   f'FROM dbo.employees;')
    rows = cursor.fetchall()
    employees = {row[0]: {'about_me': row[1], 'hobbies': row[2]} for row in rows}
    employees_embeddings = {}
    for row in rows:
        embeddings = {}
        if row[3]:
            embeddings['work_experience+projects'] = np.frombuffer(row[3], dtype=np.float32)
        if row[4]:
            embeddings['skills'] = np.frombuffer(row[4], dtype=np.float32)
        if row[5]:
            embeddings['about_me+hobbies'] = np.frombuffer(row[5], dtype=np.float32)
        employees_embeddings[row[0]] = embeddings
    cursor.execute(f'SELECT employee_id, description FROM dbo.education;')
    for row in cursor.fetchall():
        employees[row[0]]['education'] = row[1]
    cursor.execute(f'SELECT employee_id, description FROM dbo.experience;')
    for row in cursor.fetchall():
        employees[row[0]]['experience'] = row[1]
    cursor.execute(f'SELECT employee_id, description FROM dbo.projects;')
    for row in cursor.fetchall():
        employees[row[0]]['projects'] = row[1]
    cursor.execute(f'SELECT employee_id, description FROM dbo.skills;')
    for row in cursor.fetchall():
        employees[row[0]]['skills'] = row[1]
    return employees


def put_filtered_offers_list_values(cursor, offers, condition):
    if condition == 'active':
        condition_string = 'WHERE jo.active=1'
    elif condition == 'actual':
        condition_string = 'WHERE jo.is_embedding_current=0 OR jo.is_embedding_current IN NULL'
    else:
        condition_string = ''
    cursor.execute(f'SELECT ex.job_offer_id, ex.description FROM dbo.extra_skills ex JOIN dbo.job_offers jo '
                   f'ON ex.job_offer_id = jo.id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['extra_skills'] = row[1]
    cursor.execute(f'SELECT r.job_offer_id, r.description FROM dbo.requirements r JOIN dbo.job_offers jo '
                   f'ON r.job_offer_id = jo.id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['requirements'] = row[1]
    cursor.execute(f'SELECT oi.job_offer_id, i.name FROM dbo.industries i JOIN dbo.job_offer_industries oi '
                   f'ON oi.industry_id = i.id JOIN dbo.job_offers jo ON jo.id = oi.job_offer_id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['branches'] = row[1]
    cursor.execute(f'SELECT l.job_offer_id, l.level_id FROM dbo.job_offer_levels l JOIN dbo.job_offers jo '
                   f'ON l.job_offer_id = jo.id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['levels'] = row[1]
    cursor.execute(f'SELECT ct.job_offer_id, ct.contract_type_id FROM dbo.job_offer_contract_types ct '
                   f'JOIN dbo.job_offers jo ON ct.job_offer_id = jo.id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['contract_types'] = row[1]
    cursor.execute(f'SELECT f.job_offer_id, f.employment_form_id FROM dbo.job_offer_employment_forms f '
                   f'JOIN dbo.job_offers jo ON f.job_offer_id = jo.id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['forms'] = row[1]
    cursor.execute(f'SELECT l.job_offer_id, l.localization_id FROM dbo.job_offer_localizations l '
                   f'JOIN dbo.job_offers jo ON l.job_offer_id = jo.id {condition_string};')
    for row in cursor.fetchall():
        offers[row[0]]['localizations'] = row[1]


def get_filtered_offers(cursor: pyodbc.Cursor, condition):
    if condition == 'active':
        condition_string = 'WHERE jo.active = 1'
    elif condition == 'actual':
        condition_string = 'WHERE jo.is_embedding_current = 0 OR jo.is_embedding_current IS NULL'
    else:
        condition_string = ''
    cursor.execute(f'SELECT id, offer_name, salary_from, duties, description, duties_embeddings, '
                   f'description_embeddings, skills_embeddings FROM dbo.job_offers {condition_string};')
    rows = cursor.fetchall()
    offers = {}
    offers_embeddings = {}
    for row in rows:
        offers[row[0]] = {'name': row[1], 'min_salary': row[2], 'duties': row[3], 'description': row[4]}
        embeddings = {}
        if row[5]:
            embeddings['duties'] = np.frombuffer(row[5], dtype=np.float32)
        if row[6]:
            embeddings['description'] = np.frombuffer(row[6], dtype=np.float32)
        if row[7]:
            embeddings['requirements+extra_skills'] = np.frombuffer(row[7], dtype=np.float32)
        offers_embeddings[row[0]] = embeddings
    put_filtered_offers_list_values(cursor, offers, condition)
    return offers, offers_embeddings


def get_employers_to_update(cursor: pyodbc.Cursor):
    cursor.execute(f'SELECT id, about_me, interests FROM dbo.employees '
                   f'WHERE is_embedding_current = 0 OR is_embedding_current IS NULL;')
    rows = cursor.fetchall()
    employees = {row[0]: {'about_me': row[1], 'hobbies': row[2]} for row in rows}
    cursor.execute(f'SELECT ed.employee_id, ed.description FROM dbo.education ed JOIN dbo.employees e '
                   f'ON ed.employee_id = e.id WHERE e.is_embedding_current = 0 OR is_embedding_current IS NULL;')
    for row in cursor.fetchall():
        employees[row[0]]['education'] = row[1]
    cursor.execute(f'SELECT ex.employee_id, ex.description FROM dbo.experience ex JOIN dbo.employees e '
                   f'ON ex.employee_id = e.id WHERE e.is_embedding_current = 0 OR is_embedding_current IS NULL;')
    for row in cursor.fetchall():
        employees[row[0]]['experience'] = row[1]
    cursor.execute(f'SELECT p.employee_id, p.description FROM dbo.projects p JOIN dbo.employees e '
                   f'ON p.employee_id = e.id WHERE e.is_embedding_current = 0 OR is_embedding_current IS NULL;')
    for row in cursor.fetchall():
        employees[row[0]]['projects'] = row[1]
    cursor.execute(f'SELECT s.employee_id, s.description FROM dbo.skills s JOIN dbo.employees e '
                   f'ON s.employee_id = e.id WHERE e.is_embedding_current = 0 OR is_embedding_current IS NULL;')
    for row in cursor.fetchall():
        employees[row[0]]['skills'] = row[1]
    return employees
