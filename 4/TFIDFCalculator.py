import os
import csv
import math
import json
from collections import defaultdict

inverted_index_path = "D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\3\\inverted_index.json"
processed_dir = "D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\2\\processed_documents"
output_tf_csv = "D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\4\\tf_index.csv"
output_idf_csv = "D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\4\\idf_index.csv"
output_tfidf_csv = "D:\\Repositories\\2025_ITIS_IS_11-106_ZotovAA\\4\\tfidf_index.csv"


def load_inverted_index(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_tf(processed_dir):
    tf_data = defaultdict(dict)
    doc_lengths = {}
    for filename in os.listdir(processed_dir):
        if filename.endswith(".txt"):
            try:
                # Извлекаем номер документа из имени файла (например, из "processed_1.txt" получаем "1")
                doc_id = filename.split(".")[0]  # Убираем расширение
                doc_id = doc_id.split("_")[-1]  # Берем последнюю часть после подчеркивания
                
                filepath = os.path.join(processed_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    words = f.read().split()
                    total_terms = len(words)
                    doc_lengths[doc_id] = total_terms
                    term_counts = defaultdict(int)
                    for word in words:
                        term_counts[word] += 1
                    for term, count in term_counts.items():
                        tf_data[term][doc_id] = round(count / total_terms, 6)
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {str(e)}")
                continue
    return tf_data, doc_lengths


def calculate_idf(inverted_index, total_docs):
    idf_data = {}
    for term, doc_ids in inverted_index.items():
        df = len(set(doc_ids))
        idf_data[term] = round(math.log(total_docs / (1 + df)),6)
    return idf_data


def calculate_tfidf(tf_data, idf_data, doc_ids):
    tfidf_data = defaultdict(dict)
    for term in tf_data:
        for doc_id in doc_ids:
            tf = tf_data[term].get(doc_id, 0)
            idf = idf_data.get(term, 0)
            tfidf_data[term][doc_id] = round(tf * idf,6)
    return tfidf_data


def save_matrix_to_csv(data, doc_ids, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term"] + doc_ids)
        for term in sorted(data):
            row = [term] + [data[term].get(doc_id, 0) for doc_id in doc_ids]
            writer.writerow(row)


def save_idf_to_csv(idf_data, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "idf"])
        for term in sorted(idf_data):
            writer.writerow([term, idf_data[term]])


inverted_index = load_inverted_index(inverted_index_path)
tf_data, doc_lengths = calculate_tf(processed_dir)
doc_ids = sorted(doc_lengths.keys(), key=lambda x: int(x))
total_docs = len(doc_ids)

idf_data = calculate_idf(inverted_index, total_docs)
tfidf_data = calculate_tfidf(tf_data, idf_data, doc_ids)

save_matrix_to_csv(tf_data, doc_ids, output_tf_csv)
save_idf_to_csv(idf_data, output_idf_csv)
save_matrix_to_csv(tfidf_data, doc_ids, output_tfidf_csv)
