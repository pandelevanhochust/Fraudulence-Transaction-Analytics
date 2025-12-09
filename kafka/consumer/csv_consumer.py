
import json
import logging
import os
import time

import requests

from kafka import KafkaConsumer
from kafka.errors import KafkaError

KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka:29092').split(',')
TOPIC = os.getenv('TOPIC', 'transactions')
MODEL_API_ENDPOINT = os.getenv('MODEL_API_ENDPOINT', 'http://model-service:8000/api/transactions')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = float(os.getenv('RETRY_DELAY', '2'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionConsumer:
    def __init__(self, bootstrap_servers, model_api_endpoint, topic='transactions'):
        self.bootstrap_servers = bootstrap_servers
        self.model_api_endpoint = model_api_endpoint
        self.topic = topic
        self.consumer = None
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY

    def create_consumer(self):
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None,
                group_id='fraud_detection_group',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                max_poll_records=10,
                consumer_timeout_ms=5000,
            )
            logger.info(f"Kafka consumer created successfully for topic '{self.topic}'")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return False

    def validate_transaction(self, transaction):
        required_fields = ['transaction_id', 'amount']
        
        for field in required_fields:
            if field not in transaction:
                logger.error(f"Missing required field: {field}")
                return False

        amount = transaction.get('amount')
        if amount is None:
            logger.error("Amount is None")
            return False
        
        try:
            float(amount)
        except (ValueError, TypeError):
            logger.error(f"Invalid amount type: {type(amount)}, value: {amount}")
            return False

        return True

    def send_to_model_service(self, transaction):
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.model_api_endpoint,
                    json=transaction,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    result = response.json()
                    fraud_status = "FRAUD" if result.get('prediction', 0) == 1 else "NORMAL"
                    logger.info(
                        f"✓ Sent to Model Service: {transaction.get('transaction_id', 'unknown')} "
                        f"- Amount: ${transaction.get('amount', 0):.2f} - Status: {fraud_status}"
                    )
                    return True
                elif response.status_code == 422:
                    logger.error(f"Validation error for transaction {transaction.get('transaction_id', 'unknown')}: {response.text}")
                    return False
                else:
                    logger.warning(f"Model Service returned {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout sending to Model Service (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error to Model Service (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

        logger.error(f"Failed to send transaction to Model Service after {self.max_retries} attempts")
        return False

    def start_consuming(self):
        logger.info("Starting Kafka consumer...")
        logger.info(f"Model Service endpoint: {self.model_api_endpoint}")

        retry_count = 0
        while retry_count < self.max_retries:
            try:
                if not self.create_consumer():
                    retry_count += 1
                    logger.warning(
                        f"Retrying consumer creation in {self.retry_delay} seconds... ({retry_count}/{self.max_retries})"
                    )
                    time.sleep(self.retry_delay)
                    continue

                logger.info("Consumer started successfully. Waiting for messages...")
                message_count = 0

                for message in self.consumer:
                    try:
                        transaction = message.value
                        message_count += 1

                        transaction_id = transaction.get('transaction_id', f'unknown_{message_count}')
                        amount = transaction.get('amount', 0)
                        logger.info(
                            f"Received message #{message_count}: {transaction_id} - Amount: ${amount:.2f}"
                        )

                        if self.validate_transaction(transaction):
                            self.send_to_model_service(transaction)
                        else:
                            logger.error(f"Invalid transaction data: {transaction}")

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message JSON: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                    time.sleep(0.1)

            except KafkaError as e:
                logger.error(f"Kafka error: {e}")
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds... ({retry_count}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached. Exiting...")
                    break

            except KeyboardInterrupt:
                logger.info("Received shutdown signal...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                retry_count += 1
                if retry_count < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    break
            finally:
                if self.consumer:
                    self.consumer.close()
                    logger.info("Consumer closed")

        logger.info("Consumer stopped")


if __name__ == "__main__":
    consumer = TransactionConsumer(
        bootstrap_servers=KAFKA_BROKERS,
        model_api_endpoint=MODEL_API_ENDPOINT,
        topic=TOPIC
    )
    consumer.start_consuming()
