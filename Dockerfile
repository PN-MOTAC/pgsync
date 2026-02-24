FROM python:3.12-slim AS build

ARG WORKDIR=/code
ARG EXAMPLE_NAME=airbnb
ENV EXAMPLE_NAME=$EXAMPLE_NAME

# Create and switch to workdir
RUN mkdir -p "$WORKDIR"
WORKDIR "$WORKDIR"

# Install git and curl (required for pip install from git+ URL and schema download)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY ./examples/ ./examples
COPY ./docker/wait-for-it.sh ./wait-for-it.sh
COPY ./docker/runserver.sh ./runserver.sh

# Copy plugins directory into the container
COPY ./plugins $WORKDIR/plugins

# Copy the entire project for local installation
COPY . $WORKDIR/

# Install pgsync from local source
RUN pip install --no-cache-dir .

# Make scripts executable
RUN chmod +x wait-for-it.sh runserver.sh

# Set PYTHONPATH to point to the parent directory of the plugins folder
ENV PYTHONPATH="$WORKDIR"
