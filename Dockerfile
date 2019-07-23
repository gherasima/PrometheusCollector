FROM python:alpine3.7

ENV PYTHONUNBUFFERED=1

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["collector-app.py"]

# docker build --rm -t gherasima/collector .
