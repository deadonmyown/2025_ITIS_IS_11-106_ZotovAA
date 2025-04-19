import math
import csv
from collections import defaultdict

import pymorphy3

morph = pymorphy3.MorphAnalyzer()


def compute_query_vector(query_terms, idf):
    term_counts = defaultdict(int)
    for term in query_terms:
        term_counts[term] += 1
    total_terms = len(query_terms)
    tfidf_q = {}
    for term, count in term_counts.items():
        tf = count / total_terms
        tfidf_q[term] = tf * idf.get(term, 0)
    return tfidf_q


def cosine_similarity(vec1, vec2):
    dot = sum(vec1[t] * vec2.get(t, 0) for t in vec1)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)


def search(query, tfidf_index, idf, doc_ids, top_k=10):
    query_terms = list(map(lambda token: morph.parse(token)[0].normal_form,query.lower().split()))
    query_vector = compute_query_vector(query_terms, idf)
    results = []
    for doc_id in doc_ids:
        doc_vector = {term: tfidf_index[term].get(doc_id, 0) for term in tfidf_index}
        score = cosine_similarity(query_vector, doc_vector)
        if score > 0:
            results.append((doc_id, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

def load_tfidf_index(tfidf_path):
    tfidf_index = defaultdict(dict)
    with open(tfidf_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)[1:]
        for row in reader:
            term = row[0]
            for doc_id, value in zip(headers, row[1:]):
                tfidf_index[term][doc_id] = float(value)
    return tfidf_index, headers


def load_idf(idf_path):
    idf = {}
    with open(idf_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            idf[row[0]] = float(row[1])
    return idf


if __name__ == "__main__":
    tfidf_index, doc_ids = load_tfidf_index("D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\4\\tfidf_index.csv")
    idf = load_idf("D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\4\\idf_index.csv")
    while True:
        query = input("Введите запрос (чтобы выйти введите 'exit'): ")
        if query.lower() == "exit":
            break
        results = search(query, tfidf_index, idf, doc_ids)
        if not results:
            print("Ничего не найдено.")
        else:
            print("Результаты:")
            for doc_id, score in results:
                print(f"Документ {doc_id} — релевантность: {score:.4f}")
