import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse


class WebCrawler:
    def __init__(self):
        self.base_url = 'https://www.championat.com'
        self.request_url = 'https://www.sport-express.ru/news/'
        self.class_attribute = 'se-material__title se-material__title--size-middle'
        self.pages_folder_name = os.path.dirname(__file__) + '/pages'
        self.index_file_name = os.path.dirname(__file__) + '/index.txt'
        os.mkdir(self.pages_folder_name)

    def find_pages(self):
        links = []
        for i in range(1, 5):
            request_url = self.request_url + f'page{i}'
            page = urllib.request.urlopen(request_url)
            soup = BeautifulSoup(page, 'html.parser')
            for div in soup.findAll('div', {'class': self.class_attribute}):
                link = div.find('a')['href']
                if link:
                    links.append(link)
        return links

    def get_text_from_page(self, url):
        request = requests.get(url)
        request.encoding = request.apparent_encoding
        if request.status_code == 200:
            soup = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')
            bad_tags = ['style', 'link', 'script']
            for tag in soup.find_all(bad_tags):
                tag.extract()
            return str(soup)
        return None

    def download_pages(self, count: int = 100):
        links = list(set(self.find_pages()))
        index_file = open(self.index_file_name, 'w', encoding='utf-8')
        i = 1
        for link in links:
            if i <= count:
                text = self.get_text_from_page(link)
                if text is None:
                    continue
                else:
                    page_name = self.pages_folder_name + '/выкачка_' + str(i) + '.html'
                    page = open(page_name, 'w', encoding='utf-8')
                    page.write(text)
                    page.close()
                    index_file.write(str(i) + ' ' + link + '\n')
                    i += 1
            else:
                break
        index_file.close()


if __name__ == '__main__':
    crawler = WebCrawler()
    crawler.download_pages()