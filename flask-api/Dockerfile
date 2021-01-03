FROM python:3-slim

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y build-essential

COPY pyproject.toml ./

COPY poetry.lock ./

ENV PATH="${PATH}:/root/.local/bin"

RUN pip install --upgrade pip

RUN pip install --user poetry

RUN poetry install

COPY ./ .

CMD ["poetry","run","uwsgi","uwsgi.ini"]