FROM python:3.12-alpine

RUN apk update && apk add --no-cache \
    curl \
    ncurses

RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.4

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . /app/

RUN poetry install --without=dev