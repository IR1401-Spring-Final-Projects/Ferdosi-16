import io
import os.path
import logging

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup


class HTML2CSV:

    @staticmethod
    def filter_poems(tag):
        return tag.name == 'span' and tag.has_attr('class') and 'content_text' in tag.get('class')

    @staticmethod
    def filter_labels(tag):
        return tag.name == 'h2' and tag.has_attr('class') and 'content_h2' in tag.get('class')

    @staticmethod
    def filter_poems_labels(tag):
        return HTML2CSV.filter_poems(tag) or HTML2CSV.filter_labels(tag)

    @staticmethod
    def extract_to(directory, file_name):

        logging.info('Extracting...')

        with io.open(os.path.join(directory, 'shahnameh-ferdosi.htm'), 'r', encoding='utf-8') as file:
            html = file.read()

        soup = BeautifulSoup(html, 'html.parser')
        poems_and_labels = soup.find_all(HTML2CSV.filter_poems_labels)

        skip_labels = {'مشخصات کتاب', 'معرفی'}
        buffered_text = None

        dataset = []

        label = None
        for item in tqdm(poems_and_labels):

            if HTML2CSV.filter_labels(item):
                label = item.get_text()
            elif not (HTML2CSV.filter_poems(item) and label) or label in skip_labels:
                continue

            text = item.get_text()
            if '****' not in text:
                buffered_text = text
                continue

            if buffered_text:
                text = ' '.join([buffered_text, text])
                buffered_text = None

            mesras = [sp.strip() for sp in text.split('****')]
            dataset.append({'text': ' - '.join(mesras), 'labels': label})

        pd.DataFrame(dataset).to_csv(os.path.join(directory, file_name), index=False)
        logging.info('Extracted.')
