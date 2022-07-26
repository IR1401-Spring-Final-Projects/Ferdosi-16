# syntax=docker/dockerfile:1
FROM python:3.10

WORKDIR /app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src/ /app/
COPY ./entrypoint.sh /code/

RUN ["chmod", "+x", "./entrypoint.sh"]

CMD ./entrypoint.sh
