import os
from abc import ABC, abstractmethod
from api import search_pb2
from services import elastic


class SearchResult:
    _method = None
    
    def __init__(self, similarity=None, max_results=20):
        self.similarity = similarity
        self.max_results = max_results

    @abstractmethod
    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        pass

    @property
    def method(self):
        return self._method


class BooleanSearchResult(SearchResult):
    _method = 'boolean'

    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        return search_pb2.DocumentResponse(
            items=[
                search_pb2.DocumentResponseItem(
                    document=search_pb2.Document(
                        id=f'{i}',
                        mesra1=poem.split('-')[0].strip(),
                        mesra2=poem.split('-')[1].strip(),
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(self.similarity.get_similar_by_boolean(query, self.max_results))
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
                        mesra1=poem.split('-')[0].strip(),
                        mesra2=poem.split('-')[1].strip(),
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(self.similarity.get_similar_by_tfidf(query, self.max_results))
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
                        mesra1=poem.split('-')[0].strip(),
                        mesra2=poem.split('-')[1].strip(),
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(self.similarity.get_similar_by_word_embedding(query, self.max_results))
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
                        mesra1=poem.split('-')[0].strip(),
                        mesra2=poem.split('-')[1].strip(),
                        label=label,
                    ),
                    reason_of_choice=self._method,
                    similarity=similarity,
                ) for i, (poem, label, similarity) in
                enumerate(self.similarity.get_similar_by_sentence_embedding(query, self.max_results))
            ]
        )


class ElasticSearchResult(SearchResult):
    _method = 'elastic'

    def __init__(self):
        super().__init__()
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