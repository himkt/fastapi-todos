FROM python:3.8.12-slim-buster as builder

RUN pip3 install poetry==1.1.7
RUN pip3 install -U setuptools==57.5.0

RUN apt update -y && apt install -y build-essential default-libmysqlclient-dev

WORKDIR /work

COPY pyproject.toml ./
COPY poetry.lock    ./
COPY poetry.toml    ./
COPY fastapi_todos  ./fastapi_todos

RUN poetry install --no-dev


FROM python:3.8.12-slim-buster as runner

COPY --from=builder /usr/include/mariadb /usr/include/mariadb
COPY --from=builder /usr/lib             /usr/lib

WORKDIR /work

COPY --from=builder /work/.venv ./.venv
COPY --from=builder /work/fastapi_todos ./fastapi_todos

CMD [ \
     ".venv/bin/gunicorn", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", ":3000", \
     "fastapi_todos.app:create_app()" \
]
