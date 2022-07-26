from concurrent import futures
import logging
import os

import grpc
from api import search_pb2, search_pb2_grpc, query_expansion_pb2, query_expansion_pb2_grpc
from extractor import HTML2CSV
from server import search_server, query_exapnsion_server


def serve(_port, _grpc_workers):
    logging.info('Starting server...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_grpc_workers))
    search_pb2_grpc.add_SearchServicer_to_server(search_server.SearchServer(), server)
    query_expansion_pb2_grpc.add_QueryExpandServicer_to_server(query_exapnsion_server.QueryExpansionServer(), server)
    server.add_insecure_port(f'[::]:{_port}')
    server.start()
    server.wait_for_termination()
    logging.info('Server started.')
    logging.info(f'Listening on port {_port} with {_grpc_workers} workers.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    HTML2CSV.extract_to('resources/', 'shahnameh-labeled.csv')
    port = os.getenv('GRPC_PORT', '50051')
    grpc_workers = int(os.getenv('MAX_GRPC_WORKERS', 2))
    serve(port, grpc_workers)

