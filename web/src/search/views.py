from django.shortcuts import render
from django.views import View
from client.grpc_client import GrpcClient
from api import search_pb2, query_expansion_pb2
from google.protobuf.json_format import MessageToDict


class TestClass(View):
    def get(self, request):
        if "query" in request.GET:
            query = request.GET["query"]
            grpc_cli = GrpcClient()
            query_response = grpc_cli.search_stub.Retrieve(search_pb2.SearchRequest(query=query))
            query_expansion_response = grpc_cli.query_expansion_stub.Expand(
                query_expansion_pb2.ExpandRequest(query=query))
            return render(request, "search/main.html", {
                "search": MessageToDict(query_response),
                "expand": MessageToDict(query_expansion_response)
            })
        return render(request, "search/main.html")
