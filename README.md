# Transaction Fraud Detection System

A real-time fraud detection pipeline that processes transactions through Kafka, applies ML models for fraud detection, and displays results in a modern web dashboard.

## Architecture

```
Producer → Kafka → Consumer → Model Service → Backend API → Frontend
```

### Components

1. **Kafka Producer**: Generates and sends transaction data to Kafka topic
2. **Kafka Consumer**: Consumes transactions from Kafka and forwards to Model Service
3. **Model Service**: Applies fraud detection ML model and enriches transactions
4. **Backend API**: Stores enriched transactions in SQLite database
5. **Frontend**: React dashboard with Ant Design UI for visualization

## Quick Start

### 1. Start the system

```bash
docker-compose up -d
```

This will start all services:
- Zookeeper (port 2181)
- Kafka (port 9092)
- Producer
- Consumer
- Model Service (port 8001)
- Backend API (port 8000)
- Frontend (port 3000)

### 4. Access the dashboard

Open your browser and navigate to:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Model Service**: http://localhost:8001

### 5. Check logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f producer
docker-compose logs -f consumer
docker-compose logs -f model-service
docker-compose logs -f backend
```

### 6. Stop the system

```bash
docker-compose down
```

To also remove volumes (database data):

```bash
docker-compose down -v
```

## Environment Variables

### Producer
- `KAFKA_BROKERS`: Kafka broker addresses (default: `kafka:29092`)
- `TOPIC`: Kafka topic name (default: `transactions`)
- `DELAY_BETWEEN_MESSAGES`: Delay in seconds between messages (default: `1`)

### Consumer
- `KAFKA_BROKERS`: Kafka broker addresses (default: `kafka:29092`)
- `TOPIC`: Kafka topic name (default: `transactions`)
- `MODEL_API_ENDPOINT`: Model service URL (default: `http://model-service:8000/api/transactions`)

### Model Service
- `MODEL_PATH`: Path to model file (default: `xgboost_model.pkl`)
- `BACKEND_API_URL`: Backend API URL (default: `http://backend:8000/api/transactions`)

### Backend
- `DB_PATH`: SQLite database path (default: `transactions.db`)

### Frontend
- `VITE_API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)

## API Endpoints

### Backend API (port 8000)

- `GET /api/transactions?page=1&size=20` - Get paginated transactions
- `POST /api/transactions` - Create new transaction
- `DELETE /api/transactions/{id}` - Delete transaction
- `DELETE /api/transactions` - Clear all transactions
- `GET /api/transactions/summary` - Get transaction summary
- `GET /api/health` - Health check

### Model Service (port 8001)

- `POST /api/transactions` - Process transaction for fraud detection
- `POST /predict` - Direct prediction endpoint
- `GET /health` - Health check

## Development

### Running services individually

#### Producer
```bash
cd kafka/producer
docker build -t producer .
docker run --network fraud-detection-network -e KAFKA_BROKERS=kafka:29092 producer
```

#### Consumer
```bash
cd kafka/consumer
docker build -t consumer .
docker run --network fraud-detection-network \
  -e KAFKA_BROKERS=kafka:29092 \
  -e MODEL_API_ENDPOINT=http://model-service:8000/api/transactions \
  consumer
```

#### Backend
```bash
cd backend
docker build -t backend .
docker run -p 8000:8000 --network fraud-detection-network backend
```

#### Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
.
├── docker-compose.yaml          # Main Docker Compose configuration
├── README.md                    # This file
├── backend/                     # Backend API service
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/                    # React frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│       └── FraudDetectionDashboard.jsx
├── kafka/
│   ├── producer/                # Kafka producer
│   │   ├── Dockerfile
│   │   ├── csv_producer.py
│   │   └── requirements.txt
│   └── consumer/               # Kafka consumer
│       ├── Dockerfile
│       ├── csv_consumer.py
│       └── requirements.txt
└── model/                       # ML model service
    ├── Dockerfile
    ├── fraud_detection.py
    ├── model_service.py
    ├── config.py
    ├── schemas.py
    ├── requirements.txt
    └── xgboost_model.pkl       # Model file (not in repo)
```

