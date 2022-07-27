from time import sleep
from typing import List
import pandas as pd
from api import search_pb2, search_pb2_grpc
from server import search_result
from services.similarities import Similarities
from services.clustring import Clustering


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

        self.clustering = Clustering(df, 9, _checkpoint='resources/clustering')

    def Retrieve(self, request, context) -> search_pb2.SearchResponse:
        query = request.query

        search_results = {}
        for provider in self.search_result_providers:
            search_results[provider.method] = provider.get_search_result(query)

        classification_result = search_pb2.ClassificationResponse(
            items=[
                search_pb2.ClassificationResponseItem(
                    id=1,
                    label='',
                    similarity=0.0,
                )
            ]
        )

        cid, (counts, labels) = self.clustering.predict_cluster(query)
        cluster_result = search_pb2.ClusteringResponse(
            cluster_id=cid,
            most_repeated_labels=[
                search_pb2.ClusteringResponseItem(
                    id=i,
                    label=label,
                    count=count,
                ) for i, (count, label) in enumerate(zip(counts, labels))
            ]
        )

        important_names_result = search_pb2.ImportantNameResponse(
            items=[
                search_pb2.ImportantNameResponseItem(
                    id=1,
                    name='',
                    type='شخصیت',
                    page_rank=0.0,
                    hits_rank=0.0,
                )
            ]
        )

        return search_pb2.SearchResponse(
            search_results=search_results,
            classification=classification_result,
            clustering=cluster_result,
            important_names=important_names_result
        )
