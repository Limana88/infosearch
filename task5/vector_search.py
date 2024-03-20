import re
import numpy as np
from os import listdir, path
from pymorphy2 import MorphAnalyzer
from nltk.tokenize import word_tokenize
from scipy.spatial import distance


class VectorSearch:
    def __init__(self):
        self.index_file_name = path.dirname(__file__) + '/index.txt'
        self.tf_idf_folder_name = path.dirname(__file__) + '/lemmas_tf_idf'
        self.links = dict()
        self.lemmas = []
        self.matrix = None
        self.read_links()
        self.read_lemmas()
        self.read_tf_idf()
        self.morph = MorphAnalyzer()

    def read_links(self):
        with open(self.index_file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.split(' ')
                self.links[key] = value

    def read_lemmas(self):
        file_names = listdir(self.tf_idf_folder_name)
        with open(self.tf_idf_folder_name + '/' + file_names[0], 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                self.lemmas.append(line.split(' ')[0])

    def read_tf_idf(self):
        file_names = listdir(self.tf_idf_folder_name)
        self.matrix = np.zeros((len(file_names), len(self.lemmas)))
        for file_name in file_names:
            file_number = int(re.search('\\d+', file_name)[0])
            with open(self.tf_idf_folder_name + '/' + file_name, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i in range(len(lines)):
                    lemma, idf, tf_idf = lines[i].split(' ')
                    self.matrix[file_number - 1][i] = float(tf_idf)

    def vectorize(self, query: str) -> np.ndarray:
        vector = np.zeros(len(self.lemmas))
        tokens = word_tokenize(query)
        for token in tokens:
            parsed_token = self.morph.parse(token)[0]
            lemma = parsed_token.normal_form if parsed_token.normalized.is_known else token.lower()
            if lemma in self.lemmas:
                vector[self.lemmas.index(lemma)] = 1
        return vector

    def search(self, query: str) -> list:
        vector = self.vectorize(query)
        similarities = dict()
        i = 1
        for row in self.matrix:
            dist = 1 - distance.cosine(vector, row)
            if dist > 0:
                similarities[i] = dist
            i += 1
        sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)
        result = [(self.links[str(doc[0])], doc[1]) for doc in sorted_similarities]
        return result