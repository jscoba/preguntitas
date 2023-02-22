FROM python:3.9-slim-bullseye

ENV DJANGO_SETTINGS_MODULE=quiz_server.test_settings
RUN apt-get update
RUN apt-get install make
WORKDIR /app

COPY . /app

RUN make installdeps

CMD make test