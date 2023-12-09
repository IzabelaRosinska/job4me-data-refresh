import random

from utils.file_reader import read_json, write_json


def get_counter():
    companies = read_json('../files/companies.json')
    offers = read_json('../files/offers.json')
    counter = {key: 0 for key in companies}
    for offer in offers.values():
        counter[offer['company']] += 1
    return counter


def check_companies():
    companies = read_json('../files/companies.json')
    offers_counter = get_counter()
    counter = {}
    i = 0
    j = 0
    for name, company in companies.items():
        j += 1
        if not company['description']:
            print(name, offers_counter[name])
            i += 1
    print(i, j)
    print(counter)


def find_single_offer_companies():
    companies = read_json('../files/companies.json')
    offers = read_json('../files/offers.json')
    counter = {key: 0 for key in companies}
    for offer in offers.values():
        counter[offer['company']] += 1
    sizes = {}
    for company, number in counter.items():
        sizes.setdefault(number, 0)
        sizes[number] += 1
        if number < 1:
            print(company)
    print(sizes)


def remove_small_companies(percent: float = 0.8):
    companies = read_json('../files/companies.json')
    offers = read_json('../files/offers.json')
    counter = {key: 0 for key in companies}
    for offer in offers.values():
        counter[offer['company']] += 1
    new_companies = {name: company for name, company in companies.items() if counter[name] > 1 or counter[name] > 0 and random.uniform(0, 1) > percent}
    write_json('../files/companies.json', new_companies, 2)


def get_companies_branches(companies: dict, offers: dict, return_companies_branches=False):
    companies_branches = {name: set() for name in companies}
    for offer in offers.values():
        if offer['company'] in companies:
            companies_branches[offer['company']] |= set(offer['branches'])
    branches_dict = {'IT': set(), 'Zdrowie': set(), 'Sprzedaż': set(), 'Administracja Biura': set()}
    for company, branches in companies_branches.items():
        for branch in branches:
            branches_dict[branch].add(company)
    return branches_dict, companies_branches if return_companies_branches else branches_dict


def change_company():
    companies = read_json('../files/companies.json')
    offers = read_json('../files/offers.json')
    branches_dict = get_companies_branches(companies, offers)
    for offer in offers.values():
        if not offer['company'] in companies:
            possible_companies = branches_dict[offer['branches'][0]]
            for branch in offer['branches'][1:]:
                possible_companies &= branches_dict[branch]
            if possible_companies:
                offer['company'] = random.choice(list(possible_companies))
    write_json('../files/offers.json', offers)


def check_offers_companies():
    companies = read_json('../files/companies.json')
    offers = read_json('../files/offers.json')
    for offer in offers.values():
        if offer['company'] not in companies:
            print(offer)


def generate_phone_number(long_chance: float = 0.3):
    phone = ''
    if random.uniform(0, 1) <= long_chance:
        phone += '+48 '
    phone += str(random.randint(1, 9))
    for _ in range(8):
        phone += str(random.randint(0, 9))
    return phone


def fill_phone():
    companies = read_json('../files/companies.json')
    for company in companies.values():
        if not company['contact_phone']:
            company['contact_phone'] = generate_phone_number()
    write_json('../files/companies.json', companies)


def generate_email(name: str):
    email = name.lower().replace(' s.a.', '').replace(' sp. z o.o.', '').replace(' SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ'.lower(), '').replace(' spółka z o.o.', '').replace(' sp. z o. o.', '').replace(' sp. z o.o', '').replace(' sp.k.', '').replace(' sp. k.', '').replace(' sp z o o', '').replace(' ', '_') + "@"
    domains = ['gmail.com', 'op.pl', 'wp.pl']
    email += random.choice(domains)
    return email


def fill_email():
    companies = read_json('../files/companies.json')
    for name, company in companies.items():
        if not company['contact_email']:
            company['contact_email'] = generate_email(name)
            print(name, company['contact_email'])
    write_json('../files/companies.json', companies, 2)


def remove_small_and_without_description():
    companies = read_json('../files/companies.json')
    counter = get_counter()
    new_companies = {}
    for name, company in companies.items():
        if company['description'] and counter[name] > 2:
            new_companies[name] = company
    write_json('../files/companies.json', new_companies)


remove_small_and_without_description()
change_company()
