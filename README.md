# PrometheusCollector
Spin up a Grafana and a Prometheus collector of the given version using a custom retention hours inside of a docker container.

Usage:
git clone git@github.com:gherasima/PrometheusCollector.git<br>
cd PrometheusCollector\n
pip3 install -r requirements.txt\n
python3 run.py -v TAG -r HOURS
