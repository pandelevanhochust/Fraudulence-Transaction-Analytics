FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY csv_consumer.py .

CMD ["python", "csv_consumer.py"]
