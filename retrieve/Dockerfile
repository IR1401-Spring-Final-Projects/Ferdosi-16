# syntax=docker/dockerfile:1
FROM huggingface/transformers-pytorch-cpu:latest

WORKDIR /app/

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY src/ /app/
COPY resources/ /app/resources/

CMD ["python3", "main.py"]
