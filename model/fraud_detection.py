import os
from datetime import datetime

import requests
from config import settings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from model_service import model_service
from schemas import HealthCheck, PredictionInput, PredictionOutput

app = FastAPI(title=settings.api_title, version="1.0.0")
TRANSACTION_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api/transactions")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Service running", "timestamp": datetime.utcnow()}

@app.get("/health", response_model=HealthCheck)
async def health():
    return HealthCheck(status="healthy", timestamp=datetime.utcnow(), model_loaded=model_service.is_model_loaded(), kafka_connected=True)

@app.post("/predict", response_model=PredictionOutput)
async def predict(input: PredictionInput):
    try:
        return model_service.predict(input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions")
async def process_transaction(transaction_data: dict):
    """
    Receive transaction → predict fraud → send result to Backend API
    Pipeline: Consumer → Model Service → Backend API
    """
    try:
        transaction_id = transaction_data.get('transaction_id', 'unknown')
        logger.info(f"Received transaction: {transaction_id}")
        prediction_input = PredictionInput(features=transaction_data)
        result = model_service.predict(prediction_input)

        enriched_transaction = {
            **transaction_data,
            "prediction": result.prediction,
            "fraud_probability": result.probability[0] if result.probability else result.prediction,
            "predicted_at": datetime.utcnow().isoformat()
        }

        try:
            response = requests.post(TRANSACTION_API_URL, json=enriched_transaction, timeout=10)
            if response.status_code == 200:
                logger.info(f"[✓] Sent enriched transaction to Backend API: {transaction_id}")
            else:
                logger.warning(f"[!] Failed to forward to Backend API: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"[✗] Error forwarding to Backend API: {e}")

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "prediction": result.prediction,
            "fraud_probability": result.probability[0] if result.probability else result.prediction
        }

    except Exception as e:
        logger.error(f"Prediction and forwarding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")