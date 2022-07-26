from concurrent import futures
import logging

import grpc
from api import search_pb2, search_pb2_grpc, query_expansion_pb2, query_expansion_pb2_grpc
from server import search_server


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_pb2_grpc.add_SearchServicer_to_server(search_server.SearchServer(), server)
    # query_expansion_pb2_grpc.add_QueryExpandServicer_to_server(search_server.SearchServer(), server)
    server.add_insecure_port('[::]:9201')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()