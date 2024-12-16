FROM python:3.9

# Set a working directory
ARG WORKDIR=/code
RUN mkdir $WORKDIR
WORKDIR $WORKDIR

# Install pgsync
RUN pip install git+https://github.com/toluaina/pgsync.git

# Copy necessary scripts
COPY ./docker/wait-for-it.sh wait-for-it.sh
COPY ./docker/runserver.sh runserver.sh

# Copy plugins directory into the container
COPY ./plugins $WORKDIR/plugins

# Set permissions for scripts
RUN chmod +x wait-for-it.sh
RUN chmod +x runserver.sh

# Set PYTHONPATH to point to the plugins folder
ENV PYTHONPATH="$WORKDIR/plugins"