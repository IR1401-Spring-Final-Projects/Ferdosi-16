from typing import List
from api import search_pb2, search_pb2_grpc
from server import search_result


class SearchServer(search_pb2_grpc.SearchServicer):
    def __init__(self):
        self.search_result_providers: List[search_result.SearchResult] = [
            search_result.TfidfSearchResult(),
            search_result.BooleanSearchResult(),
            search_result.WordEmbeddingSearchResult(),
            search_result.SentEmbeddingSearchResult(),
            search_result.ElasticSearchResult(),
        ]

    def Retrieve(self, request, context) -> search_pb2.SearchResponse:
        query = request.query
        search_results = {}
        for provider in self.search_result_providers:
            search_results[provider.method] = provider.get_search_result(query)

        return search_pb2.SearchResponse(search_results=search_results)
