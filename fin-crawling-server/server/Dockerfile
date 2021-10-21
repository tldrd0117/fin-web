FROM python:3.9.7-slim

WORKDIR /usr/src/app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y jq
RUN apt-get install -y curl
# RUN apt-get install -y libffi-dev

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
CMD ["poetry","run","uvicorn","app.main:app", "--reload", "--host=0.0.0.0", "--port=8000"]
# CMD ["poetry","run","uvicorn","app.main:app", "--reload"]
# ARG BUILD_FLAVOR
# RUN echo "$BUILD_FLAVOR"
# RUN if [ "$BUILD_FLAVOR" = "DEV" ]; then echo "hello"; else echo "bye"; fi
# RUN if [ "$BUILD_FLAVOR" = "DEV" ]; then poetry run uvicorn app.main:app --reload --host=0.0.0.0 --port=8000; else poetry run uvicorn app.main:app --uds /usr/src/app/sock/uvicorn.sock; fi
# CMD ["poetry","run","uvicorn","app.main:app"]
