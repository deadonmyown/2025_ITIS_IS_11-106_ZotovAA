import os
import re
import pymorphy3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

morph = pymorphy3.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))
punctuation = set(string.punctuation)

def clean_text(text):
    text = re.sub(r'\d+', '', text) # убираю даты, цифры и спецсимвы
    text = re.sub(r'[^\w\s-]', ' ', text) # убираю лишнюю пунктуацию (кроме дефиса в словах)
    text = ' '.join([word for word in text.split() if len(word) > 1 or word in {'я', 'в', 'у', 'с', 'к', 'о'}]) # удаляю одиночные букв (кроме "я", "в" и т.п.)
    return text

def process_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = clean_text(text.lower())

    tokens = word_tokenize(text.lower(), language='russian')
    
    processed_tokens = []
    for token in tokens:
        if token not in stop_words and token not in punctuation and not token.isnumeric():
            lemma = morph.parse(token)[0].normal_form
            processed_tokens.append(lemma)
    
    return processed_tokens

def process_all_documents(input_dir, output_dir):
    """Обработка всех документов в директории"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):  # предполагаем текстовые файлы
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"processed_{filename}")
            
            processed_tokens = process_document(input_path)
            
            # Сохранение обработанного документа
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(' '.join(processed_tokens))
            print(f"Обработан и сохранён: {output_path}")

# Пример использования
if __name__ == "__main__":
    input_directory = "D:\\Repositories\\ITIS\\2025_ITIS_IS_11-106_ZotovAA\\1\\NAZVANIE1\\pages"  # папка с исходными документами
    output_directory = "processed_documents"  # папка для обработанных документов
    
    process_all_documents(input_directory, output_directory)
