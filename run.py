import argparse
import docker
import sys


def run_prometheus_container(version, retention):
    client = docker.from_env()
    image = "prom/prometheus:" + version
    prometheus_config = f" --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.console.libraries=/usr/share/prometheus/console_libraries --web.console.templates=/usr/share/prometheus/consoles --storage.tsdb.retention={retention}h"

    try:
        client.images.pull(image)
    except docker.errors.ImageNotFound:
        sys.exit('Prometheus Tag/Version does not exist')

    try:
        int(retention)
    except ValueError:
        sys.exit('Prometheus retention hours is not valid, please supply an integer.')

    try:
        client.containers.run(image, prometheus_config, ports={'9090/tcp': 9090},  detach=True, name='Prometheus_' + version)
    except docker.errors.APIError as e:
        print("Can't start container!")
        print(e)
        sys.exit()

    print('Prometheus container is up and available at http://127.0.0.1:9090')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Spin up a prometheus collector of the given version inside of a docker container.')
    parser.add_argument('version')
    parser.add_argument('retention')
    args = parser.parse_args()

    version = args.version
    retention = args.retention

    if version and retention:
        run_prometheus_container(version, retention)
