FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app

COPY . /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry  && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT [ "bash", "/app/entry.sh" ]