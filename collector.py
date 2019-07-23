import argparse
import docker


def run_container(image):
    client = docker.from_env()
    client.containers.run(image, ports={'8787/tcp': 8787},  detach=True)


def main(version, retention):
    run_container("gherasima/collector")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Spin up a prometheus collector inside a docker container.')
    parser.add_argument('version')
    parser.add_argument('retention')
    args = parser.parse_args()

    version = args.version
    retention = args.retention

    if version and retention:
        main(version, retention)
