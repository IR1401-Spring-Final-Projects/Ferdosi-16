import os
import grpc

from api import search_pb2_grpc, query_expansion_pb2_grpc


class GrpcClient:

    def __init__(self):
        server_address = os.getenv('GRPC_SERVER_ADDRESS', 'localhost:9201')
        self.channel = grpc.insecure_channel(server_address)
        self.search_stub = search_pb2_grpc.SearchStub(self.channel)
        self.query_expansion_stub = query_expansion_pb2_grpc.QueryExpandStub(self.channel)

    def destroy_channel(self):
        self.channel.close()
