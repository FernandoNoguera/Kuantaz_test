FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y gcc \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && apt-get remove -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python3", "app.py"]

