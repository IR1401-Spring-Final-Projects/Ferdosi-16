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
                    'fuzziness': 'AUTO'
                }
            }
        })
