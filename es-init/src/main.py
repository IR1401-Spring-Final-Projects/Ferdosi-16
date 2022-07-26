import os
from extractor import Extractor, HTML2CSV


def main():
    url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
    print('Starting...')
    extractor = Extractor(url)
    HTML2CSV.extract_to()
    extractor.run()
    print('Done')


if __name__ == '__main__':
    main()
