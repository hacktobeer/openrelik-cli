FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    iputils-ping \
    curl \
    jq \
    netcat-openbsd

RUN pip install uv

ADD . /app
WORKDIR /app

RUN chmod +x main.py
RUN echo 'alias openrelik-cli="/app/main.py"' >> /root/.bashrc

RUN uv sync --all-groups

ENV PYTHONPATH=/app

