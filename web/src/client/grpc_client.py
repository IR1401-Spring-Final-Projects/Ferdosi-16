import os
import grpc

from api import search_pb2_grpc, query_expansion_pb2_grpc


class GrpcClient:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GrpcClient, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        server_address = os.getenv('GRPC_SERVER_ADDRESS', 'localhost:50051')
        self.channel = grpc.insecure_channel(server_address)
        self.search_stub = search_pb2_grpc.SearchStub(self.channel)
        self.query_expansion_stub = query_expansion_pb2_grpc.QueryExpandStub(self.channel)

    def destroy_channel(self):
        self.channel.close()