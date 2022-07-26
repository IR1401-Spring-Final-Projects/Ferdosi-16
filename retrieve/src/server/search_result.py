from abc import abstractmethod
from retrieve.src.api import search_pb2
from retrieve.src.services.similarities import Similarities

import pandas as pd


class SearchResult:
    _method = None

    @abstractmethod
    def get_search_result(self, query) -> search_pb2.DocumentResponse:
        pass

    @property
    def method(self):
        return self._method


df = pd.read_csv('es-init/resources/shahnameh-labeled.csv')
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
                        id=i,
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
                        id=i,
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
                        id=i,
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
