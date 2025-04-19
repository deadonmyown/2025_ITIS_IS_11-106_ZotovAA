import os
import re
from collections import defaultdict
from typing import List, Set, Dict
import json

class SearchEngine:
    def __init__(self, processed_docs_dir: str):
        self.processed_docs_dir = processed_docs_dir
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self.documents: List[str] = []
        
    def build_inverted_index(self):
        """Создание инвертированного индекса из обработанных документов"""
        for filename in os.listdir(self.processed_docs_dir):
            if filename.endswith('.txt'):
                doc_path = os.path.join(self.processed_docs_dir, filename)
                doc_id = filename
                self.documents.append(doc_id)
                
                with open(doc_path, 'r', encoding='utf-8') as f:
                    terms = f.read().split()
                    for term in terms:
                        self.inverted_index[term].add(doc_id)
        
        # Сортировка терминов по алфавиту
        self.inverted_index = dict(sorted(self.inverted_index.items()))
        
    def save_index(self, output_file: str):
        """Сохранение инвертированного индекса в файл"""
        # Преобразуем множества в списки для сериализации
        serializable_index = {term: list(docs) for term, docs in self.inverted_index.items()}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_index, f, ensure_ascii=False, indent=2)
            
    def load_index(self, input_file: str):
        """Загрузка инвертированного индекса из файла"""
        with open(input_file, 'r', encoding='utf-8') as f:
            loaded_index = json.load(f)
            self.inverted_index = {term: set(docs) for term, docs in loaded_index.items()}
            # Восстанавливаем список документов
            self.documents = list(set(doc for docs in self.inverted_index.values() for doc in docs))
    
    def print_index_stats(self):
        """Вывод статистики индекса"""
        print("\nСтатистика инвертированного индекса:")
        print(f"Всего документов: {len(self.documents)}")
        print(f"Всего уникальных терминов: {len(self.inverted_index)}")
        print("\nПервые 10 терминов в индексе:")
        for i, (term, docs) in enumerate(list(self.inverted_index.items())[:10]):
            print(f"{term}: встречается в {len(docs)} документах")
    
    def parse_query(self, query: str) -> List[str]:
        """Парсинг запроса и преобразование в постфиксную нотацию"""
        # Заменяем русские операторы на английские
        query = query.replace('ИЛИ', '|').replace('И', '&').replace('НЕ', '!')
        
        # Разбиваем запрос на токены
        tokens = re.findall(r'[&\|!]|\w+', query)
        return tokens
    
    def evaluate_query(self, query: str) -> Set[str]:
        """Выполнение булева поиска по запросу с учетом приоритетов операторов"""
        tokens = self.parse_query(query)
        
        # Сначала обрабатываем все отрицания
        i = 0
        while i < len(tokens):
            if tokens[i] == '!':
                if i + 1 >= len(tokens):
                    raise ValueError("Некорректный запрос: оператор НЕ без операнда")
                term = tokens[i + 1]
                if term in ['&', '|', '!']:
                    raise ValueError("Некорректный запрос: после НЕ должен идти термин")
                tokens[i:i+2] = [set(self.documents) - self.inverted_index.get(term, set())]
            else:
                i += 1
        
        # Функция для получения приоритета оператора
        def get_priority(op):
            if op == '&':
                return 2
            elif op == '|':
                return 1
            return 0
        
        # Преобразуем в постфиксную нотацию (обратную польскую запись)
        output = []
        operators = []
        
        for token in tokens:
            if token in ['&', '|']:
                while (operators and 
                       get_priority(operators[-1]) >= get_priority(token)):
                    output.append(operators.pop())
                operators.append(token)
            else:
                if isinstance(token, str):
                    output.append(self.inverted_index.get(token, set()))
                else:
                    output.append(token)
        
        while operators:
            output.append(operators.pop())
        
        # Вычисляем результат
        stack = []
        for token in output:
            if token in ['&', '|']:
                if len(stack) < 2:
                    raise ValueError("Некорректный запрос: недостаточно операндов")
                right = stack.pop()
                left = stack.pop()
                if token == '&':
                    stack.append(left & right)
                else:
                    stack.append(left | right)
            else:
                stack.append(token)
        
        if not stack:
            raise ValueError("Некорректный запрос: пустой запрос")
        
        return stack[0]

def main():
    # Путь к директории с обработанными документами
    processed_docs_dir = "D:\\Repositories\\ITIS\\2025_ITIS_IS_11-106_ZotovAA\\2\\processed_documents"
    
    # Создаем экземпляр поисковой системы
    search_engine = SearchEngine(processed_docs_dir)
    
    # Строим инвертированный индекс
    print("Построение инвертированного индекса...")
    search_engine.build_inverted_index()
    
    # Выводим статистику индекса
    search_engine.print_index_stats()
    
    # Сохраняем индекс в файл
    index_file = "D:\\Repositories\\ITIS\\2025_ITIS_IS_11-106_ZotovAA\\3\\inverted_index.json"
    search_engine.save_index(index_file)
    print(f"\nИнвертированный индекс сохранен в файл {index_file}")
    
    # Получаем первые три термина из индекса для примеров
    example_terms = list(search_engine.inverted_index.keys())[:3]
    if len(example_terms) < 3:
        print("\nВнимание: в индексе меньше 3 терминов для тестовых запросов!")
        return
    
    # Примеры запросов с реальными терминами из индекса
    example_queries = [
        f"{example_terms[0]} & {example_terms[1]} | {example_terms[2]}",
        f"{example_terms[0]} & !{example_terms[1]} | !{example_terms[2]}",
        f"{example_terms[0]} | {example_terms[1]} | {example_terms[2]}",
        f"{example_terms[0]} | !{example_terms[1]} | !{example_terms[2]}",
        f"{example_terms[0]} & {example_terms[1]} & {example_terms[2]}"
    ]
    
    # Выполняем поиск для каждого примера
    print("\nРезультаты поиска для примеров:")
    for query in example_queries:
        try:
            results = search_engine.evaluate_query(query)
            print(f"\nЗапрос: {query}")
            print(f"Найдено документов: {len(results)}")
            if results:
                print("Документы:", sorted(results))
        except ValueError as e:
            print(f"Ошибка в запросе '{query}': {str(e)}")
    
    # Интерактивный режим
    print("\nВведите запрос для поиска (для выхода введите 'exit'):")
    while True:
        query = input("> ")
        if query.lower() == 'exit':
            break
            
        try:
            results = search_engine.evaluate_query(query)
            print(f"Найдено документов: {len(results)}")
            if results:
                print("Документы:", sorted(results))
        except ValueError as e:
            print(f"Ошибка в запросе: {str(e)}")

if __name__ == "__main__":
    main() 