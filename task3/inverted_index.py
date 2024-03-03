import re
import pymorphy2
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize


class IndexEntry:
    def __init__(self):
        self.count = 0
        self.files = []

    def update(self, count, file_number):
        self.count += count
        self.files.append(int(file_number))


def compare_index_entry(x: IndexEntry, y: IndexEntry):
    return int(x.count) - int(y.count)


class InvertedIndex:
    def __init__(self):
        self.pages_folder_name = path.dirname(__file__) + '/pages'
        self.lemmas_file_name = path.dirname(__file__) + '/lemmas.txt'
        self.inverted_index_file_name = path.dirname(__file__) + '/inverted_index.txt'
        self.morph = pymorphy2.MorphAnalyzer()
        self.lemmas = dict()
        self.index = dict()

    def read_list_of_lemmas(self):
        file = open(self.lemmas_file_name, 'r')
        lines = file.readlines()
        for line in lines:
            words = re.split('\\s+', line)
            key = words[0][:len(words[0]) - 1]
            self.lemmas[key] = []
            for i in range(1, len(words) - 1):
                self.lemmas[key].append(words[i])
        file.close()

    def get_index(self):
        for file_name in listdir(self.pages_folder_name):
            file = open(self.pages_folder_name + '/' + file_name, 'r', encoding='utf-8')
            text = BeautifulSoup(file, features='html.parser').get_text()
            list_of_words = wordpunct_tokenize(text)
            words = set()
            for word in list_of_words:
                parsed_word = self.morph.parse(word)[0]
                lemma = parsed_word.normal_form if parsed_word.normalized.is_known else word.lower()
                if lemma in self.lemmas.keys() and lemma not in words:
                    words.add(lemma)
                    word_forms = self.lemmas[lemma]
                    count = 0
                    for word_form in word_forms:
                        count += list_of_words.count(word_form)
                    if lemma not in self.index.keys():
                        self.index[lemma] = IndexEntry()
                    self.index[lemma].update(count, re.search('\\d+', file_name)[0])
            file.close()
        for key, value in self.index.items():
            value.files.sort()

    def write_index(self):
        file = open(self.inverted_index_file_name, 'w')
        for word, entry in self.index.items():
            line = word + ' (' + str(entry.count) + '):'
            for file_number in entry.files:
                line += ' ' + str(file_number)
            line += '\n'
            file.write(line)
        file.close()

    def create_index_file(self):
        self.read_list_of_lemmas()
        self.get_index()
        self.write_index()


if __name__ == '__main__':
    inverted_index = InvertedIndex()
    inverted_index.create_index_file()