from concurrent import futures
import logging
import os

import grpc
from api import search_pb2, search_pb2_grpc, query_expansion_pb2, query_expansion_pb2_grpc
from server import search_server


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_pb2_grpc.add_SearchServicer_to_server(search_server.SearchServer(), server)
    # query_expansion_pb2_grpc.add_QueryExpandServicer_to_server(search_server.SearchServer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    port = os.getenv('GRPC_PORT', '50051')
    serve(port)