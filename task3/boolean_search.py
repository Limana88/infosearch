import pymorphy2
from os import path
import re


class SearchQuery:
    def __init__(self, query: str, files: set):
        self.query = query
        self.files = files

    def __and__(self, other):
        return SearchQuery(self.query + ' & ' + other.query, self.files & other.files)

    def __or__(self, other):
        return SearchQuery(self.query + ' | ' + other.query, self.files | other.files)

    def __sub__(self, other):
        return SearchQuery(self.query + ' ! ' + other.query, self.files - other.files)


class BooleanSearch:
    def __init__(self):
        self.inverted_index_file_name = path.dirname(__file__) + '/inverted_index.txt'
        self.morph = pymorphy2.MorphAnalyzer()
        self.index = dict()
        self.tokens = dict()
        self.read_inverted_index()

    def read_inverted_index(self):
        file = open(self.inverted_index_file_name, 'r')
        lines = file.readlines()
        for line in lines:
            items = re.split('\\s+', line)
            token = items[0]
            files = set()
            files_list = []
            for i in range(2, len(items) - 1):
                files.add(int(items[i]))
                files_list.append(int(items[i]))
            self.index[token] = SearchQuery(token, files)
            self.tokens[token] = files_list
        file.close()

    def search(self, search_words):
        tokens = re.split('\\s+', search_words)
        parsed_token = self.morph.parse(tokens[0])[0]
        start_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[0].lower()
        result = SearchQuery('', set())
        if start_token in self.index.keys():
            result = self.index[start_token]
        i = 1

        if 1 < len(tokens) < 3 and tokens[0] == '!':
            word = tokens[1]
            parsed_token = self.morph.parse(word)[0]
            normal_form = parsed_token.normal_form if parsed_token.normalized.is_known else word.lower()

            if normal_form in self.index:
                new_result = self.index[normal_form]
                result |= new_result
                query_all_files = SearchQuery('', set(range(1, 101)))
                result = query_all_files - result

        else:
            while i < len(tokens):
                if tokens[i] == '&' and i + 1 < len(tokens):
                    parsed_token = self.morph.parse(tokens[i + 1])[0]
                    current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[
                        i + 1].lower()
                    if current_token in self.index.keys():
                        new_result = self.index[current_token]
                        result = result & new_result
                    i += 1
                elif tokens[i] == '|' and i + 1 < len(tokens):
                    parsed_token = self.morph.parse(tokens[i + 1])[0]
                    current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[
                        i + 1].lower()
                    if current_token in self.index.keys():
                        new_result = self.index[current_token]
                        result = result | new_result
                    i += 1
                else:
                    parsed_token = self.morph.parse(tokens[i])[0]
                    current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[i].lower()
                    if current_token in self.index.keys():
                        new_result = self.index[current_token]
                        result = result | new_result
                i += 1

        result = list(result.files)
        result.sort()
        return result


if __name__ == '__main__':
    boolean_search = BooleanSearch()

    print('Введите запрос одной строкой. Например: \nпрокомментировать & сумма \n! тарасов \nпрокомментировать | целый \nсумма & прокомментировать | целый & турция | завоевать')

    query = str(input())

    print(f'Ваш запрос = {query}')
    print(f'Результат = {boolean_search.search(query)}')
