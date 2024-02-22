import nltk
import string
import re
import pymorphy2
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


class Tokenizer:
    def __init__(self):
        self.pages_folder_name = path.dirname(__file__) + '/pages'
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('russian'))
        self.morph = pymorphy2.MorphAnalyzer()
        self.tokens = set()
        self.lemmas = dict()

    def is_correct_token(self, token):
        has_punctuation = True if any(x in string.punctuation for x in token) else False
        is_stop_word = bool(token.lower() in self.stop_words)
        is_number = bool(re.compile(r'^[0-9]+$').match(token))
        is_russian = bool(re.compile(r'^[а-яА-Я]{2,}$').match(token))
        are_stuck_words = False
        if sum(map(str.isupper, token[1:])) > 0 and (sum(map(str.islower, token[1:])) > 0 or str.islower(token[0])):
            are_stuck_words = True
        is_good_word = True if self.morph.parse(token)[0].score >= 0.5 else False
        return not has_punctuation and not is_stop_word and not is_number and is_russian and not are_stuck_words and \
            is_good_word

    def get_list_of_tokens(self):
        for page_name in listdir(self.pages_folder_name):
            html = open(self.pages_folder_name + '/' + page_name, 'r', encoding='utf-8', errors='ignore')
            text = BeautifulSoup(html, features='html.parser').get_text()
            tokens = wordpunct_tokenize(text)
            self.tokens = self.tokens | set(filter(self.is_correct_token, tokens))
            html.close()
        self.write_list_of_tokens()

    def write_list_of_tokens(self):
        tokens_file = open(path.dirname(__file__) + '/tokens.txt', 'w')
        for token in self.tokens:
            tokens_file.write(token + '\n')
        tokens_file.close()

    def group_tokens_by_lemmas(self):
        for token in self.tokens:
            parsed_token = self.morph.parse(token)[0]
            normal_form = parsed_token.normal_form if parsed_token.normalized.is_known else token.lower()
            if normal_form not in self.lemmas:
                self.lemmas[normal_form] = []
            self.lemmas[normal_form].append(token)
        self.write_list_of_lemmas()

    def write_list_of_lemmas(self):
        lemmas_file = open(path.dirname(__file__) + '/lemmas.txt', 'w')
        for lemma, tokens in self.lemmas.items():
            line = lemma + ': '
            for token in tokens:
                line += token + ' '
            line += '\n'
            lemmas_file.write(line)
        lemmas_file.close()


if __name__ == '__main__':
    tokenizer = Tokenizer()
    tokenizer.get_list_of_tokens()
    tokenizer.group_tokens_by_lemmas()