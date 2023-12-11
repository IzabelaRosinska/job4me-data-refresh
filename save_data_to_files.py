from sentence_transformers import SentenceTransformer

from utils.file_reader import *
from matching.recommendation import Recommender
from utils.utils import get_dict_part, get_json_writable_embeddings
from process_data import *


def save_labels(input_file, destination_file: str, for_offer=True, sum_to_one=True, update: bool = True):
    data = read_json(input_file)
    labels = {text_id: recommender.get_labels(text, for_offer,
                                              get_dict_part(branches_weights, text['branches'] + ['Ogólne', 'Języki']),
                                              sum_to_one) for text_id, text in tqdm(data.items())}
    update_json(destination_file, labels) if update else write_json(destination_file, labels)


def save_offers_embeddings_to_file(update: bool = False):
    offers = read_json('files/offers.json')
    offers_embeddings = get_offers_embeddings(offers, sentence_transformer)
    json_writable_embeddings = get_json_writable_embeddings(offers_embeddings)
    update_json('files/offers_embeddings.json', json_writable_embeddings) if update \
        else write_json('files/offers_embeddings.json', json_writable_embeddings)


def save_employees_embeddings_to_file(update: bool = False):
    employees = read_json('files/employees.json')
    employees_embeddings = get_offers_embeddings(employees, sentence_transformer)
    json_writable_embeddings = get_json_writable_embeddings(employees_embeddings)
    update_json('files/employees_embeddings.json', json_writable_embeddings) if update \
        else write_json('files/employees_embeddings.json', json_writable_embeddings)


def save_offers_labels():
    save_labels('files/offers.json', 'files/offers_labels.json', True, True, False)


def save_employees_labels():
    save_labels('files/employees.json', 'files/employees_labels.json', False, True, False)


labels_data, branches_weights = load_labels([('IT', 'files/labels_IT.json', 3),
                                            ('Sprzedaż', 'files/labels_sprzedaż.json', 2),
                                            ('Zdrowie', 'files/labels_zdrowie.json', 2),
                                            ('Administracja Biura', 'files/labels_AB.json', 2),
                                            ('Ogólne', 'files/labels_soft_skills.json', 1),
                                            ('Języki', 'files/labels_languages.json', 5)])


if __name__ == '__main__':
    recommender = Recommender(labels_data)
    sentence_transformer = SentenceTransformer('sentence-transformers/LaBSE')

    save_offers_labels()
    save_offers_embeddings_to_file()
    save_employees_labels()
    save_employees_embeddings_to_file()
