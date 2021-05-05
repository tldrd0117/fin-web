FROM python:3-slim

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y jq
RUN apt-get install -y curl

COPY pyproject.toml ./

COPY poetry.lock ./

ENV PATH="${PATH}:/root/.local/bin"

ENV IS_DOCKER_RUN Yes

RUN pip install --upgrade pip

RUN pip install --user poetry

RUN poetry install

COPY ./ .

# ENTRYPOINT [ "sh", "./wait-for-grid.sh" ]

# CMD ["poetry","run","uwsgi","uwsgi.ini"]
# CMD ["poetry","run","app"]
# CMD ["uwsgi","--ini","uwsgi.ini"]
CMD ["poetry","run","uwsgi","--ini","uwsgi.ini"]
