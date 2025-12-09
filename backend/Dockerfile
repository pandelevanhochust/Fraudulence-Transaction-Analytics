FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* ./
RUN if [ ! -f requirements.txt ]; then \
        echo "fastapi==0.104.1" > requirements.txt && \
        echo "uvicorn[standard]==0.24.0" >> requirements.txt && \
        echo "pydantic==2.5.0" >> requirements.txt && \
        echo "python-multipart==0.0.6" >> requirements.txt; \
    fi

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
