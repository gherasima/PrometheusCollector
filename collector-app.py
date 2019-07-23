from prometheus_client import start_http_server, Summary
import random
import time
# import argparse


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Prometheus Python collector')
    # parser.add_argument('version')
    # parser.add_argument('retention')
    # args = parser.parse_args()
    #
    # version = args.version
    # retention = args.retention
    #
    # if version and retention:
    # Start up the server to expose the metrics.
    start_http_server(8787)
    # Generate some requests.
    while True:
        process_request(random.random())
