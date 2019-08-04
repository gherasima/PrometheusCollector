# PrometheusCollector
Spin up a Grafana and a Prometheus collector of the given version using a custom retention hours inside of a docker container.

Usage:<br>
git clone git@github.com:gherasima/PrometheusCollector.git<br>
cd PrometheusCollector<br>
pip3 install -r requirements.txt<br>
python3 run.py -v TAG -r HOURS<br>
