import os
from api import query_expansion_pb2, query_expansion_pb2_grpc
from services import elastic


class QueryExpansionServer(query_expansion_pb2_grpc.QueryExpandServicer):
    def __init__(self):
        es_host = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.es_query = elastic.ElasticSearchQuery(es_host=es_host)

    def Expand(self, request, context) -> query_expansion_pb2.ExpandResponse:
        query = request.query
        words = []
        for w in query.split():
            correct_word = self.es_query.find_word(w)
            if correct_word:
                words.append(correct_word)

        return query_expansion_pb2.ExpandResponse(
            items=[
                query_expansion_pb2.ExpandResponseItem(
                    expanded=' '.join(words),
                    confidence=1.0,
                )
            ]
        )
