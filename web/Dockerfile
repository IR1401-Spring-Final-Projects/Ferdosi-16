FROM python:3.10

WORKDIR /app/

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY src/ /app/
COPY resources/ /app/resources/

COPY entrypoint.sh /app/
RUN ["chmod", "+x", "./entrypoint.sh"]

CMD ./entrypoint.sh
