FROM python:3.10-slim

# update all depedencies
ENV DEFAULT_PACKAGES="curl git openssh-client build-essential"
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends --no-upgrade $DEFAULT_PACKAGES && \
    rm -rf /var/lib/apt/lists/*

# create working directory
WORKDIR /app

# setup poetry
RUN pip install poetry && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./

ARG INSTALL_DEV_DEPS
RUN --mount=type=ssh  \
    if [ -z "$INSTALL_DEV_DEPS" ] ; then poetry install --only main --no-interaction ; else poetry install --no-interaction ; fi

COPY . .
ENV PYTHONPATH=.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080