FROM python:3.12-slim-bullseye

RUN apt update && apt install -y curl libpq-dev gcc

RUN curl -sSL https://install.python-poetry.org | \
    POETRY_HOME=/opt/poetry POETRY_VERSION=1.5.1 python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/
WORKDIR /app
RUN poetry install --no-root

COPY ./api /app/api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
