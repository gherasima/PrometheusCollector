import argparse
import sys
import os
import requests
import json
import time
import re

# Check for minimum Python version
required_python_min_version = (3, 4)
if sys.version_info < required_python_min_version:
    print('Error! Python minimum version {}.{} is required to run the program.\n '.format(required_python_min_version[0], required_python_min_version[1]))
    sys.exit()


# Check if we have all required modules installed
try:
    import docker
except ImportError:
    sys.exit('Docker Python module not found, please install it by running pip3 install docker')


def get_all_prometheus_tag():
    # Get all image tags
    url = 'https://registry.hub.docker.com/v1/repositories/prom/prometheus/tags'
    session = requests.Session()
    try:
        r = session.get(url)
    except:
        sys.exit(
            'Error! Can\'t get all prometheus Docker image tags! please make sure you have internet connection')
    r_json = r.json()

    # Latest major version
    v0 = []
    v1 = []
    v2 = []
    for v in r_json:
        ver = v['name']
        if re.search('rc', ver) or re.search('-', ver):
            pass
        else:
            if ver.startswith('v2'):
                v2.append(ver)
            elif ver.startswith('v1'):
                v1.append(ver)
            elif ver.startswith('0'):
                v0.append(ver)
    return {'v0': v0, 'v1': v1, 'v2': v2}


def create_docker_network(docker_network):
    client = docker.from_env()

    try:
        client.networks.list()
    except requests.exceptions.ConnectionError:
        sys.exit('Error! Docker engine is not running.')
    try:
        print('Creating Docker network')
        client.networks.create('prometheus', check_duplicate=True)
    except docker.errors.APIError:
        print('Docker network already exist')


def run_prometheus_container(version, retention, program_usage, docker_network):
    client = docker.from_env()
    image = "prom/prometheus:" + version
    prometheus_config = (" --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus " 
                        "--web.console.libraries=/usr/share/prometheus/console_libraries " 
                        "--web.console.templates=/usr/share/prometheus/consoles --storage.tsdb.retention={}h".format(retention))

    try:
        client.containers.list()
    except requests.exceptions.ConnectionError:
        sys.exit('Error! Docker engine is not running.')

    try:
        print('Trying to pull Prometheus image with tag ' + version)
        client.images.pull(image)
    except (docker.errors.ImageNotFound, requests.exceptions.HTTPError):
        sys.exit('Error pulling image! Prometheus Tag/Version does not exist or can\'t connect to Docker hub, please make sure you have internet connection and the Prometheus Tag/Version is correct: https://hub.docker.com/r/prom/prometheus/tags\n' + program_usage)

    try:
        int(retention)
    except ValueError:
        sys.exit('Error! Prometheus retention hours is not valid, please supply an integer.')

    try:
        client.containers.run(image, prometheus_config, ports={'9090/tcp': 9090},  detach=True, name='prometheus', network=docker_network)
    except docker.errors.APIError as e:
        print("Can't Prometheus start container!")
        print(e)
        sys.exit()

    print('Prometheus container is up and available at http://127.0.0.1:9090')


def run_grafana_containers(docker_network):
    client = docker.from_env()
    image = "grafana/grafana:latest"

    try:
        client.containers.list()
    except requests.exceptions.ConnectionError:
        sys.exit('Error! Docker engine is not running.')

    try:
        print('Trying to pull Grafana latest image')
        client.images.pull(image)
    except (docker.errors.ImageNotFound, requests.exceptions.HTTPError):
        sys.exit('Error pulling image! Please make sure you have internet connection.')

    try:
        grafana_config = {
            'GF_SECURITY_ADMIN_PASSWORD': 'secret',
        }
        client.containers.run(image, ports={'3000/tcp': 3000}, environment=grafana_config, detach=True, name='grafana', network=docker_network)
    except docker.errors.APIError as e:
        print("Can't Grafana start container!")
        print(e)
        sys.exit()

    while True:
        try:
            # Check if Grafana is running
            post_headers = {"Content-Type": "application/json"}
            url = 'http://127.0.0.1:3000'
            session = requests.Session()
            session.auth = ('admin', 'secret')
            r = session.get(url, headers=post_headers)

            # Create datasource
            post_headers = {"Content-Type": "application/json"}
            post_data = {"name": "Prometheus", "type": "prometheus", "url": "http://prometheus:9090",
                         "access": "proxy", "basicAuth": False, "isDefault": True}
            url = 'http://127.0.0.1:3000' + '/api/datasources/'
            session = requests.Session()
            session.auth = ('admin', 'secret')
            r = session.post(url, data=json.dumps(post_data), headers=post_headers)
            if r.status_code != 200: print('Warning! Datasource create failed!')
            # Create dashboard
            with open('dash.json') as dash_file:
                data_dict = json.load(dash_file)
            post_headers = {"Content-Type": "application/json"}
            url = 'http://127.0.0.1:3000' + '/api/dashboards/db'
            session = requests.Session()
            session.auth = ('admin', 'secret')
            r = session.post(url, data=json.dumps(data_dict), headers=post_headers)
            if r.status_code != 200: print('Warning! Dashboard create failed!')
            break
        except:
            time.sleep(1)

    print('Grafana container is up and available at http://127.0.0.1:3000\nUser: admin Password: secret')


if __name__ == '__main__':
    program_name = os.path.basename(__file__)
    program_usage='Prometheus version and retention hours are required to run the program\nFor example: {} -v v2.11.1 -r 24\nYou can run {} -h for more info'.format(program_name, program_name)
    parser = argparse.ArgumentParser(description='Spin up a Grafana and a Prometheus collector of the given version inside of a docker container.', usage=program_usage)
    parser.add_argument("-v", "--version", help='Prometheus version/tag from https://hub.docker.com/r/prom/prometheus/tags', type=str, required=True)
    parser.add_argument("-r", "--retention", help="Prometheus retention in hours", type=int, required=True)
    args = parser.parse_args()

    version = args.version
    retention = args.retention

    if version and retention:

        if version == 'v1':
            print('*' * 70)
            print('Please run the program with one of the following Prometheus version:')
            print('*' * 70)
            all_tag = get_all_prometheus_tag()
            for v in all_tag['v1']:
                print(v)
            sys.exit()
        elif version == 'v2':
            print('*' * 70)
            print('Please run the program with one of the following Prometheus version:')
            print('*' * 70)
            all_tag = get_all_prometheus_tag()
            for v in all_tag['v2']:
                print(v)
            sys.exit()
        elif version == 'v0':
            print('*' * 70)
            print('Please run the program with one of the following Prometheus version:')
            print('*' * 70)
            all_tag = get_all_prometheus_tag()
            for v in all_tag['v2']:
                print(v)
            sys.exit()


        create_docker_network('prometheus')
        run_prometheus_container(version, retention, program_usage, 'prometheus')
        run_grafana_containers('prometheus')
