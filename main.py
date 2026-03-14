import os
import time
import requests
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from confluent_kafka import Producer

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# --- MongoDB Configuration ---
class MongoRepository:
    def __init__(self):
        uri = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/"
        self.client = MongoClient(uri)
        self.collection = self.client[os.getenv('MONGO_DB')]["price_history"]

    def save(self, data):
        data["created_at"] = datetime.now()
        self.collection.insert_one(data)

# --- Kafka Configuration ---
kafka_config = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'client.id': 'broker-market-data-api'
}
producer = Producer(kafka_config)
TOPIC_NAME = 'trading-assets-market-data-v1'

def delivery_report(err, msg):
    """Callback for Kafka producer to report message delivery status."""
    if err is not None:
        logger.error(f"Kafka delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] - Key: {msg.key().decode('utf-8')}")

# --- Watchlist ---
WATCHLIST = [
    "PETR4", "PETR3", "VALE3", "ITUB4", "BBDC4", "BBDC3", "BBAS3", "SANB11", "ITSA4", "BPAC11",
    "MGLU3", "LREN3", "ABEV3", "NTCO3", "RADL3", "HAPV3", "RDOR3", "ASAI3", "CRFB3", "JBSS3",
    "ELET3", "ELET6", "CMIG4", "EQTL3", "CPLE6", "ENGI11", "SBSESP", "VBBR3", "RAIZ4", "UGPA3",
    "GGBR4", "CSNA3", "USIM5", "SUZB3", "KLBN11", "WEGE3", "EMBR3", "TOTS3", "RENT3", "HYPE3",
    "MXRF11", "HGLG11", "KNIP11", "XPLG11", "BTLG11", "VISC11", "KNCR11", "HGRU11", "BOVA11", "IVVB11"
]

def run_ingestion():
    logger.info("Market data ingestion job started")
    
    token = os.getenv("BRAPI_TOKEN")
    mongo = MongoRepository()
    
    for ticker in WATCHLIST:
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url)
            response.raise_for_status()
            
            result = response.json()["results"][0]
            
            # 1. Data Mapping
            payload = {
                "ticker": result.get("symbol"),
                "name": result.get("longName"),
                "short_name": result.get("shortName"),
                "price": result.get("regularMarketPrice"),
                "volume": result.get("regularMarketVolume"),
                "updated_at": result.get("regularMarketTime")
            }

            # 2. Persistence Layer
            mongo.save(payload.copy())

            # 3. Event Streaming (Publishing)
            producer.produce(
                topic=TOPIC_NAME,
                key=ticker,
                value=json.dumps(payload).encode('utf-8'),
                callback=delivery_report
            )

            producer.poll(0)
            time.sleep(0.5) # Rate limiting / Anti-throttle

        except Exception as e:
            logger.error(f"Error processing ticker {ticker}: {e}")

    producer.flush()
    logger.info("Ingestion completed successfully: MongoDB and Kafka synchronized")

if __name__ == "__main__":
    run_ingestion()