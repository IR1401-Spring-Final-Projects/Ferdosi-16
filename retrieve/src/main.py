from concurrent import futures
import logging
import os

import grpc
from api import search_pb2, search_pb2_grpc, query_expansion_pb2, query_expansion_pb2_grpc
from retrieve.src.extractor import HTML2CSV
from server import search_server


def serve(_port, _grpc_workers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_grpc_workers))
    search_pb2_grpc.add_SearchServicer_to_server(search_server.SearchServer(), server)
    # query_expansion_pb2_grpc.add_QueryExpandServicer_to_server(search_server.SearchServer(), server)
    server.add_insecure_port(f'[::]:{_port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    HTML2CSV.extract_to('../resources/', 'shahnameh-labeled.csv')
    port = os.getenv('GRPC_PORT', '50051')
    grpc_workers = int(os.getenv('MAX_GRPC_WORKERS', 2))
    serve(port, grpc_workers)

