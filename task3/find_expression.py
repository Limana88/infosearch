import re
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

    def AND(self, posting1, posting2):
        p1 = 0
        p2 = 0
        result = list()
        while p1 < len(posting1) and p2 < len(posting2):
            if posting1[p1] == posting2[p2]:
                result.append(posting1[p1])
                p1 += 1
                p2 += 1
            elif posting1[p1] > posting2[p2]:
                p2 += 1
            else:
                p1 += 1
        return result

    def OR(self, posting1, posting2):
        p1 = 0
        p2 = 0
        result = list()
        while p1 < len(posting1) and p2 < len(posting2):
            if posting1[p1] == posting2[p2]:
                result.append(posting1[p1])
                p1 += 1
                p2 += 1
            elif posting1[p1] > posting2[p2]:
                result.append(posting2[p2])
                p2 += 1
            else:
                result.append(posting1[p1])
                p1 += 1
        while p1 < len(posting1):
            result.append(posting1[p1])
            p1 += 1
        while p2 < len(posting2):
            result.append(posting2[p2])
            p2 += 1
        return result

    def NOT(self, posting):
        result = list()
        i = 1
        for item in posting:
            while i < item:
                result.append(i)
                i += 1
            else:
                i += 1
        else:
            while i <= 100:
                result.append(i)
                i += 1
        return result

    def find_substrings_with_parentheses(self, expr):
        result = []
        stack = []
        for i, char in enumerate(expr):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if stack:
                    start_index = stack.pop()
                    result.append(expr[start_index:i + 1])
        return result

    def search(self, search_words):
        # tokens = re.split('\\s+', search_words)

        # subexpressions = self.find_substrings_with_parentheses(search_words)
        #
        # for expr in subexpressions:
        #     tokens = re.split('\\s+', expr)
        #     tokens = [s.replace('(', '').replace(')', '').replace('((', '').replace('))', '') for s in tokens]
        #     # print(tokens)
        #
        #     for index in range(len(tokens)):
        #         if tokens[index] != 'NOT' and tokens[index] != 'AND' and tokens[index] != 'OR':
        #             tokens[index] = self.tokens[tokens[index]]
        #
        #
        #     for token in tokens:
        #         match token:
        #             case 'NOT':
        #                 indexes_of_not = [index for index, value in enumerate(tokens) if value == 'NOT']
        #                 for i in range(len(indexes_of_not)):
        #                     result = self.NOT(tokens[i + 1])
        #                     tokens[i] = result
        #                     tokens.pop(i + 1)
        #             case 'AND':
        #                 indexes_of_and = tokens.index(token)
        #                 # for i in range(len(indexes_of_and)):
        #                 result = self.AND(tokens[indexes_of_and - 1], tokens[indexes_of_and + 1])
        #                 tokens[indexes_of_and - 1] = result
        #                 tokens.pop(indexes_of_and)
        #                 tokens.pop(indexes_of_and)
        #             case 'OR':
        #                 indexes_of_or = tokens.index(token)
        #                 # for i in range(len(indexes_of_or)):
        #                 result = self.OR(tokens[indexes_of_or - 1], tokens[indexes_of_or + 1])
        #                 tokens[indexes_of_or - 1] = result
        #                 tokens.pop(indexes_of_or)
        #                 tokens.pop(indexes_of_or)
        # case _:
        #     print(tokens)

        # print(tokens)

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
                elif tokens[i] == '!' and i + 1 < len(tokens):
                    parsed_token = self.morph.parse(tokens[i + 1])[0]
                    current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[
                        i + 1].lower()
                    if current_token in self.index.keys():
                        new_result = self.index[current_token]
                        result |= new_result
                        query_all_files = SearchQuery('', set(range(1, 101)))
                        result = query_all_files - result
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

    # print('! тарасов')
    # print(boolean_search.search('! тарасов'))
    # print('сумма & прокомментировать')
    # print(boolean_search.search('сумма & прокомментировать'))
    # print('целый & турция & кондратюк')
    # print(boolean_search.search('целый & турция & кондратюк'))
    # print('сумма & прокомментировать | целый & турция & кондратюк')
    # print(boolean_search.search('целый & турция & кондратюк | сумма & прокомментировать | кататься '))
    print('Введите запрос одной строкой. Например: \nпрокомментировать & сумма \n! тарасов \nпрокомментировать | целый \nсумма & прокомментировать | целый & турция & кондратюк | кататься')

    query = str(input())

    print(f'Ваш запрос = {query}')
    print(f'Результат = {boolean_search.search(query)}')
