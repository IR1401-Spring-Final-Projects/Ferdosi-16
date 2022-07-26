import io
from tqdm import tqdm
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch


class Extractor:

    def __init__(self, es_host):
        with io.open('resources/shahnameh-ferdosi.htm', 'r', encoding='utf-8') as file:
            self.html = file.read()
        self.es = Elasticsearch(hosts=es_host)
        self.skip_labels = ['مشخصات کتاب', 'معرفی']

    @staticmethod
    def filter_poems(tag):
        return tag.name == 'span' and tag.has_attr('class') and 'content_text' in tag.get('class')

    @staticmethod
    def filter_labels(tag):
        return tag.name == 'h2' and tag.has_attr('class') and 'content_h2' in tag.get('class')

    @staticmethod
    def filter_poems_labels(tag):
        return Extractor.filter_poems(tag) or Extractor.filter_labels(tag)

    def write_to_es(self, mesra1, mesra2, label):
        doc = {
            'mesra1': mesra1,
            'mesra2': mesra2,
            'beyt': ' '.join([mesra1, mesra2]),
            'label': label,
        }
        self.es.index(index='ferdosi', body=doc)

    def write_word_to_es(self, word, count):
        doc = {
            'search_field': ' '.join([word] * count),
            'word': word
        }
        self.es.index(index='words', body=doc)

    def extract(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        poems_and_labels = soup.find_all(self.filter_poems_labels)

        all_words = dict()

        buffered_text = None

        label = None
        for item in tqdm(poems_and_labels):
            if Extractor.filter_labels(item):
                label = item.get_text()
            elif Extractor.filter_poems(item) and label and label not in self.skip_labels:
                text = item.get_text()
                if '****' not in text:
                    buffered_text = text
                    continue

                if buffered_text:
                    text = ' '.join([buffered_text, text])
                    buffered_text = None

                mesras = text.split('****')
                self.write_to_es(mesras[0], mesras[1], label)
                for w in mesras[0].split() + mesras[1].split():
                    if w in all_words:
                        all_words[w] += 1
                    else:
                        all_words[w] = 1

        for word in all_words:
            self.write_word_to_es(word, all_words[word])

    def run(self):
        try:
            self.es.indices.get(index='ferdosi')
            print('Index already exists')
        except:
            print('Extracting...')
            self.extract()



