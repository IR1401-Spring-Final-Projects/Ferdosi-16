from pprint import pprint

from elasticsearch import Elasticsearch


class ElasticSearchQuery:

    def __init__(self, es_host):
        self.es = Elasticsearch(hosts=es_host)

    def search(self, query):
        return self.es.search(index='ferdosi', query={
            'match': {
                'beyt': {
                    'query': query,
                    'fuzziness': 'AUTO',
                }
            }
        })

    def find_word(self, word):
        results = self.es.search(index='words', query={
            'match': {
                'search_field': {
                    'query': word,
                    'fuzziness': 'AUTO',
                }
            }
        })['hits']['hits']

        return results[0]['_source']['word'] if len(results) > 0 else None
