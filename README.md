# Broker Market Data API

Microservice responsible for feeding the **My Broker B3** ecosystem with real-time data from the Brazilian financial market. It fetches asset prices from the Brapi API, persists the history in MongoDB, and publishes events to a Kafka topic for downstream services.

> This service is part of a series of articles documenting the **My Broker B3** ecosystem.
> Follow the full series on [dev.to/rvneto](https://dev.to/rvneto).

---

## Architecture and Data Flow

```
[Brapi API] ---> [broker-market-data-api] ---> [MongoDB: price_history]
                         |
                         +---> [Kafka: trading-assets-market-data-v1]
                                        |
                              [broker-asset-api] (consumer)
```

1. **Ingestion**: Worker iterates a watchlist of 50 assets (Blue Chips, REITs, ETFs)
2. **Fetch**: Individual requests to Brapi API respecting free plan rate limits
3. **Persistence**: Full payload stored in MongoDB for historical analysis and audit
4. **Streaming**: Price events published to Kafka topic for downstream consumers
5. **Scheduling**: Runs every 30 minutes (configurable), executes immediately on startup

---

## Tech Stack

| Technology | Usage |
| :--- | :--- |
| **Python 3.12+** | Service runtime |
| **MongoDB** | Historical price persistence |
| **Apache Kafka** (confluent-kafka) | Async event streaming |
| **Brapi API** | Real-time B3 asset data source |
| **Schedule** | Periodic task orchestration |

---

## Kafka Payload

**Topic:** `trading-assets-market-data-v1`
**Key:** ticker symbol (e.g. `PETR4`)

```json
{
  "ticker": "PETR4",
  "name": "Petroleo Brasileiro S.A. - Petrobras",
  "short_name": "PETROBRAS PN",
  "price": 35.50,
  "volume": 15234567,
  "updated_at": 1714234567
}
```

---

## Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| **BRAPI_TOKEN** | Brapi API token (required) | — |
| **MONGO_HOST** | MongoDB host | localhost |
| **MONGO_PORT** | MongoDB port | 27017 |
| **MONGO_DB** | MongoDB database name | market_data_db |
| **KAFKA_BOOTSTRAP_SERVERS** | Kafka broker address | localhost:9092 |
| **KAFKA_TOPIC** | Kafka topic to publish | trading-assets-market-data-v1 |
| **SYNC_INTERVAL_MINUTES** | Sync interval in minutes | 30 |

> **BRAPI_TOKEN** has no default value and must be explicitly provided.

---

## Local Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in your BRAPI_TOKEN
python main.py
```

## Running with Docker

```bash
docker build -t broker-market-data-api .
```

```bash
docker run \
  -e BRAPI_TOKEN=your_token_here \
  -e MONGO_HOST=broker-market-data-db \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  broker-market-data-api
```

---

*This project is part of the My Broker B3 ecosystem for microservices architecture studies.*
