FROM python:3.10

WORKDIR /app/

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY src/ /app/
COPY resources/ /app/resources/

CMD ["python", "main.py"]
