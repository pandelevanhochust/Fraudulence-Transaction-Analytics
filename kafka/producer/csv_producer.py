import csv
import json
import logging
import os
import time
import uuid
from datetime import datetime

from kafka.errors import KafkaError

from kafka import KafkaProducer

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:29092").split(",")
TOPIC = os.getenv("TOPIC", "transactions")
DELAY_BETWEEN_MESSAGES = float(os.getenv("DELAY_BETWEEN_MESSAGES", "1"))
CSV_FILE = os.getenv("CSV_FILE", "test.csv")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CSVTransactionProducer:
    def __init__(self, bootstrap_servers, topic="transactions"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.create_producer()

    def create_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x, default=str).encode("utf-8"),
                key_serializer=lambda x: x.encode("utf-8") if x else None,
                acks="all",
                retries=3,
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432,
            )
            logger.info(f"Kafka producer created successfully for topic '{self.topic}'")
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            raise

    def clean_numeric_value(self, value):
        if value is None or value == "":
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        value_str = str(value).strip().strip('"').replace(",", ".")
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return 0.0

    def clean_boolean_value(self, value):
        if isinstance(value, bool):
            return value
        value_str = str(value).strip().upper()
        return value_str in ("TRUE", "1", "YES", "T")

    def process_csv_row(self, row):
        transaction_id = row.get("transaction_id")
        if not transaction_id:
            device_id = row.get("device_id", "unknown")
            timestamp = row.get("local_timestamp", str(time.time()))
            transaction_id = f"{device_id}_{int(time.time() * 1000)}"

        timestamp_str = row.get("local_timestamp", "")
        if not timestamp_str:
            timestamp_str = datetime.now().isoformat()
        else:
            try:
                if " " in timestamp_str:
                    date_part, time_part = timestamp_str.split(" ", 1)
                    if "/" in date_part:
                        from dateutil import parser

                        timestamp_str = parser.parse(timestamp_str).isoformat()
                    else:
                        timestamp_str = datetime.now().isoformat()
                else:
                    timestamp_str = datetime.now().isoformat()
            except:
                timestamp_str = datetime.now().isoformat()

        transaction = {
            "transaction_id": transaction_id,
            "user_id": row.get("device_id", str(uuid.uuid4())),
            "merchant_id": row.get("merchant_id", ""),
            "amount": self.clean_numeric_value(row.get("amount", 0)),
            "currency": row.get("currency", "USD"),
            "timestamp": timestamp_str,
            "local_timestamp": row.get("local_timestamp", ""),
            "time": row.get("time", ""),
            "date": row.get("date", ""),
            "day": int(self.clean_numeric_value(row.get("day", 0))),
            "month": int(self.clean_numeric_value(row.get("month", 0))),
            "week_of_year": int(self.clean_numeric_value(row.get("week_of_year", 0))),
            "quarter": int(self.clean_numeric_value(row.get("quarter", 0))),
            "payment_channel": row.get("payment_channel", ""),
            "merchant_country": row.get("merchant_country", ""),
            "mcc": row.get("mcc", ""),
            "card_present": self.clean_boolean_value(row.get("card_present", False)),
            "IP": row.get("IP", ""),
            "risk_score": self.clean_numeric_value(row.get("risk_score", 0)),
            "device_id": row.get("device_id", ""),
            "card_entry_mode": row.get("card_entry_mode", ""),
            "auth_result": row.get("auth_result", ""),
            "pin_verif_method": row.get("pin_verif_method", ""),
            "tokenised": self.clean_boolean_value(row.get("tokenised", False)),
            "recurring_flag": row.get("recurring_flag", ""),
            "cross_border": self.clean_boolean_value(row.get("cross_border", False)),
            "card_activation_age": int(
                self.clean_numeric_value(row.get("card_activation_age", 0))
            ),
            "auth_characteristics": row.get("auth_characteristics", ""),
            "message_type": row.get("message_type", ""),
            "mean_amount_30d": self.clean_numeric_value(row.get("mean_amount_30d", 0)),
            "std_amount_30d": self.clean_numeric_value(row.get("std_amount_30d", 0)),
            "max_amount_30d": self.clean_numeric_value(row.get("max_amount_30d", 0)),
            "txn_counts_1h": int(self.clean_numeric_value(row.get("txn_counts_1h", 0))),
            "txn_counts_24h": int(
                self.clean_numeric_value(row.get("txn_counts_24h", 0))
            ),
            "distinct_merchants_7d": int(
                self.clean_numeric_value(row.get("distinct_merchants_7d", 0))
            ),
            "distinct_countries_30d": int(
                self.clean_numeric_value(row.get("distinct_countries_30d", 0))
            ),
            "online_share_7d": self.clean_numeric_value(row.get("online_share_7d", 0)),
            "night_ratio_30d": self.clean_numeric_value(row.get("night_ratio_30d", 0)),
            "days_since_last_txn": int(
                self.clean_numeric_value(row.get("days_since_last_txn", 0))
            ),
            "decline_rate_30d": self.clean_numeric_value(
                row.get("decline_rate_30d", 0)
            ),
            "chargebacks_365d": int(
                self.clean_numeric_value(row.get("chargebacks_365d", 0))
            ),
            "device_diversity_30d": int(
                self.clean_numeric_value(row.get("device_diversity_30d", 0))
            ),
            "mcc_entropy_30d": self.clean_numeric_value(row.get("mcc_entropy_30d", 0)),
            "credit_util_today": self.clean_numeric_value(
                row.get("credit_util_today", 0)
            ),
            "spending_trend": self.clean_numeric_value(row.get("spending_trend", 0)),
            "term_location": row.get("term_location", ""),
            "fraud": int(self.clean_numeric_value(row.get("fraud", 0))),
        }

        return transaction

    def send_transaction(self, transaction):
        try:
            future = self.producer.send(
                self.topic, key=transaction["transaction_id"], value=transaction
            )
            record_metadata = future.get(timeout=30)
            logger.info(
                f"✓ Sent transaction {transaction['transaction_id']} "
                f"to partition {record_metadata.partition} "
                f"at offset {record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Kafka error sending transaction: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending transaction: {e}")
            return False

    def read_and_send_csv(self, csv_file_path, delay=1, max_rows=None):
        possible_paths = [
            csv_file_path,
            os.path.join("/app/data", csv_file_path),
            os.path.join("/app", csv_file_path),
            os.path.join(".", csv_file_path),
            os.path.join(os.getcwd(), csv_file_path),
        ]

        actual_path = None
        for path in possible_paths:
            if os.path.exists(path):
                actual_path = path
                break

        if not actual_path:
            logger.error(
                f"CSV file not found in any of these locations: {possible_paths}"
            )
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Files in current directory: {os.listdir('.')}")
            return

        logger.info(f"Reading CSV file: {actual_path}")
        message_count = 0
        successful_sends = 0

        try:
            with open(actual_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)

                logger.info(f"CSV Headers: {reader.fieldnames}")

                for row in reader:
                    if max_rows and message_count >= max_rows:
                        logger.info(f"Reached maximum row count: {max_rows}")
                        break

                    try:
                        transaction = self.process_csv_row(row)
                        success = self.send_transaction(transaction)

                        message_count += 1
                        if success:
                            successful_sends += 1
                            logger.info(
                                f"Transaction #{message_count}: ${transaction['amount']:.2f} "
                                f"({transaction['currency']}) - Fraud: {transaction.get('fraud', 0)}"
                            )

                        time.sleep(delay)

                    except Exception as e:
                        logger.error(f"Error processing row {message_count + 1}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
        finally:
            if self.producer:
                logger.info("Flushing remaining messages...")
                self.producer.flush()
                self.producer.close()
                logger.info(
                    f"Producer stopped. Final stats: {successful_sends}/{message_count} messages sent successfully"
                )


if __name__ == "__main__":
    logger.info(f"Using Kafka brokers: {KAFKA_BROKERS}")
    logger.info(f"CSV file: {CSV_FILE}")

    producer = CSVTransactionProducer(bootstrap_servers=KAFKA_BROKERS, topic=TOPIC)
    producer.read_and_send_csv(CSV_FILE, delay=DELAY_BETWEEN_MESSAGES)
