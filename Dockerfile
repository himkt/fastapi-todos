FROM python:3.8.12-slim-buster as builder

RUN pip3 install poetry==1.1.7
RUN pip3 install -U setuptools==57.5.0

RUN apt update -y && apt install -y build-essential default-libmysqlclient-dev

WORKDIR /work

COPY pyproject.toml ./
COPY poetry.lock    ./
COPY poetry.toml    ./

RUN poetry export -f requirements.txt -o requirements.txt --dev


FROM python:3.8.12-slim-buster as runner
COPY --from=builder  /usr/lib     /usr/lib
COPY --from=builder  /usr/bin     /usr/bin
COPY --from=builder  /usr/include /usr/include

WORKDIR /work
COPY --from=builder /work/requirements.txt ./requirements.txt
COPY ./fastapi_todos ./fastapi_todos
COPY ./pyproject.toml ./pyproject.toml

RUN pip3 install -r requirements.txt
RUN pip3 install .

CMD [ \
     "gunicorn", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", ":3000", \
     "fastapi_todos.app:create_app()" \
]
