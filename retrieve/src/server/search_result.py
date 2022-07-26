import os
from abc import ABC, abstractmethod
from api import search_pb2
from services import elastic


class SearchResult:
    _method = None

    @abstractmethod
    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        pass

    @property
    def method(self):
        return self._method


# Test for demo:
class TfidfSearchResult(SearchResult):
    _method = 'tfidf'

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id='1',
                        mesra1='مصرع ۱',
                        mesra2='مصرع ۲',
                        label='داستان ...',
                    ),
                    reason_of_choice='',  # The reason we chose this specific document for this query
                    # if not important, leave it empty
                    similarity=0.5,  # The similarity of this document to the query
                )
            ]
        )


class ElasticSearchResult(SearchResult):
    _method = 'elastic'

    def __init__(self):
        es_host = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.es_query = elastic.ElasticSearchQuery(es_host=es_host)

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        results = self.es_query.search(query)
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id=r['_id'],
                        mesra1=r['_source']['mesra1'],
                        mesra2=r['_source']['mesra2'],
                        label=r['_source']['label'],
                    ),
                    similarity=r['_score'],
                ) for r in results['hits']['hits']
            ]
        )