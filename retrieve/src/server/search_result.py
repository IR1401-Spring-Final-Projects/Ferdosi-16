import os
from abc import ABC, abstractmethod
from api import search_pb2
from services import elastic
from services.similarities import Similarities

import pandas as pd


class SearchResult:
    _method = None

    @abstractmethod
    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        pass

    @property
    def method(self):
        return self._method


df = pd.read_csv('resources/shahnameh-labeled.csv')
search_model = Similarities(df)


class BooleanSearchResult(SearchResult):
    _method = 'boolean'

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id=i,
                        mesra1=poem.split(' [SEP] ')[0],
                        mesra2=poem.split(' [SEP] ')[1],
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(search_model.get_similar_by_boolean(query, 100))
            ]
        )


class TfidfSearchResult(SearchResult):
    _method = 'tfidf'

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id=f'{i}',
                        mesra1=poem.split(' [SEP] ')[0],
                        mesra2=poem.split(' [SEP] ')[1],
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(search_model.get_similar_by_tfidf(query, 100))
            ]
        )


class WordEmbeddingSearchResult(SearchResult):
    _method = 'word_embedding'

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id=f'{i}',
                        mesra1=poem.split(' [SEP] ')[0],
                        mesra2=poem.split(' [SEP] ')[1],
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(search_model.get_similar_by_word_embedding(query, 100))
            ]
        )


class SentEmbeddingSearchResult(SearchResult):
    _method = 'sent_embedding'

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id=f'{i}',
                        mesra1=poem.split(' [SEP] ')[0],
                        mesra2=poem.split(' [SEP] ')[1],
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(search_model.get_similar_by_sentence_embedding(query, 100))
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