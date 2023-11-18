from tqdm import tqdm

from matching.recommendation import Recommender
from utils.file_reader import read_json, write_json


def analyze_branches(recommender: Recommender, branches_weights):

    offers = read_json('../files/offers.json')

    new_offers = {}

    for offer_id, offer in tqdm(offers.items()):
        recognized = {branch: recommender.get_labels(offer, True, {branch: weight}, False) for branch, weight in
                      branches_weights.items()}
        branches = [branch for branch in branches_weights if
                    sum([val for key, val in recognized[branch].items() if key not in ['trener', 'rekrutacja']]) >= 15]
        if branches:
            offer["branches"] = branches
            new_offers[offer_id] = offer

    write_json('../files/offers.json', new_offers)
