from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def get_embeddings(data_to_process: dict, sections_to_process: list[list[str]], transformer=None):
    if not transformer:
        transformer = SentenceTransformer('sentence-transformers/LaBSE')
    embeddings = {}
    for data_id, data in tqdm(data_to_process.items()):
        data_embeddings = {}
        for keys in sections_to_process:
            text_to_process = "\n".join([('\n'.join(data[key]) if isinstance(data[key], list) else data[key])
                                         for key in keys if key in data if data[key]])
            if text_to_process:
                data_embeddings['+'.join(keys)] = transformer.encode(text_to_process)
        embeddings[data_id] = data_embeddings
    return embeddings


def get_offers_embeddings(offers, transformer=None) -> dict:
    sections = [['duties'], ['description'], ['requirements', 'extra_skills']]
    return get_embeddings(offers, sections, transformer)


def get_employees_embeddings(employees, transformer=None) -> dict:
    sections = [['work_experience', 'projects'], ['about_me', 'hobbies'], ['skills']]
    return get_embeddings(employees, sections, transformer)
