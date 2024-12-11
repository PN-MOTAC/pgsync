FROM python:3.9
ARG WORKDIR=/code
RUN mkdir $WORKDIR
WORKDIR $WORKDIR

# Install pgsync
RUN pip install git+https://github.com/toluaina/pgsync.git

# Add necessary scripts
COPY ./docker/wait-for-it.sh wait-for-it.sh
COPY ./docker/runserver.sh runserver.sh

# Set permissions for scripts
RUN chmod +x wait-for-it.sh
RUN chmod +x runserver.sh