from matching.recommendation import Recommender
from utils.file_reader import read_json, load_labels

employees = read_json('files/employees.json')

labels_data, branches_weights = load_labels([('IT', 'files/labels_IT.json', 3),
                                             ('Sprzedaż', 'files/labels_sprzedaż.json', 2),
                                             ('Zdrowie', 'files/labels_zdrowie.json', 2),
                                             ('Administracja Biura', 'files/labels_AB.json', 2),
                                             ('Ogólne', 'files/labels_soft_skills.json', 1),
                                             ('Języki', 'files/labels_languages.json', 5)])

offers = read_json('files/offers.json')
offers_labels = read_json('files/offers_labels.json')
offers_embeddings = read_json('files/offers_embeddings.json')

recommender = Recommender(labels_data)
recommender.load_offers(offers, branches_weights,
                        labels=offers_labels,
                        embeddings=offers_embeddings)

result = recommender.get_offers_ranking(employees['13'], {}, branches_weights)
print(result)
for position in result[:10]:
    print(offers[position]['name'], offers_labels[position])
print(recommender.get_labels(employees['21'], False, branches_weights))
