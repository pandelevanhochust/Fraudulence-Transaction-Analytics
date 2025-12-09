FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY csv_producer.py .

# Default command - will use CSV_FILE env var or default to test.csv
CMD ["python", "csv_producer.py"]
