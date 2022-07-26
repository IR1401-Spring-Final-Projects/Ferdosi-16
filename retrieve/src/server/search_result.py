from abc import ABC, abstractmethod
from api import search_pb2


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
                        id=1,
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
