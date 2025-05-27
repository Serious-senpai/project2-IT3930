# Reference: https://docs.docker.com/reference/dockerfile/
FROM python:3.12.9-alpine AS builder

RUN python -m venv /venv \
    && apk update \
    && apk add gcc libc-dev g++ libffi-dev libxml2 unixodbc-dev

COPY . /app
WORKDIR /app
RUN rm -rf .github/ .frontend/ && /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12.9-alpine AS runner

RUN apk --no-cache add curl

COPY scripts/odbc-alpine.sh /tmp/odbc.sh
RUN /tmp/odbc.sh

COPY --from=builder /venv /venv
COPY --from=builder /app /app

WORKDIR /app
ENTRYPOINT ["/venv/bin/python", "main.py", "--cors"]
