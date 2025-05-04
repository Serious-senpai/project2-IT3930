# Reference: https://docs.docker.com/reference/dockerfile/
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    python-is-python3 \
    python3 \
    python3-pip \
    python3-venv

COPY scripts/odbc.sh /tmp/odbc.sh
RUN chmod +x /tmp/odbc.sh
RUN bash /tmp/odbc.sh

RUN python3 -m venv /venv
COPY dev-requirements.txt /tmp/dev-requirements.txt
RUN /venv/bin/pip install -r /tmp/dev-requirements.txt
