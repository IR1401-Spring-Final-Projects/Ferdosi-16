from typing import List
import pandas as pd
from api import search_pb2, search_pb2_grpc
from server import search_result
from services.similarities import Similarities


class SearchServer(search_pb2_grpc.SearchServicer):
    def __init__(self):
        df = pd.read_csv('resources/shahnameh-labeled.csv')
        similarity = Similarities(df)
        self.search_result_providers: List[search_result.SearchResult] = [
            search_result.TfidfSearchResult(similarity),
            search_result.BooleanSearchResult(similarity),
            search_result.WordEmbeddingSearchResult(similarity),
            search_result.SentEmbeddingSearchResult(similarity),
            search_result.ElasticSearchResult(),
        ]

    def Retrieve(self, request, context) -> search_pb2.SearchResponse:
        query = request.query
        search_results = {}
        for provider in self.search_result_providers:
            search_results[provider.method] = provider.get_search_result(query)

        return search_pb2.SearchResponse(search_results=search_results)
