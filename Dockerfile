FROM fedora:40

RUN dnf update -y \
    && dnf install -y \
    python3.12 \
    ncurses \
    curl 

RUN curl -sSL https://install.python-poetry.org | python3.12 - --version 1.8.4

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . /app/

RUN poetry install --without=dev

CMD ["poetry", "run", "python", "src/cli.py"]