# Broker Market Data API 📈

This microservice is the component responsible for feeding the **My Broker B3** ecosystem with real-time data from the Brazilian financial market. It acts as an ingestor that consumes information from the external Brapi API and distributes it for historical persistence and price broadcasting via Kafka topics to update the system bases.

## 🏗️ Architecture and Data Flow

According to the system's technical design, this service performs the following data flow:

1.  **Ingestion**: The Worker iterates through a **Watchlist** of 50 assets (Blue Chips, REITs/FIIs, and ETFs).
2.  **Consumption**: Performs individual requests to the Brapi API, respecting the one-asset-per-call limit of the free tier.
3.  **Historical Persistence**: Stores the full payload in **MongoDB** (`broker_market_data_db`) for future analysis and auditing.
4.  **Kafka Topic Publishing**: Broadcasts messages with updated price information to the `trading-assets-market-data-v1` topic, to be consumed by downstream services.

## 🚀 Tech Stack

- **Python 3.12+**
- **MongoDB**: Document-oriented database for price history.
- **Brapi API**: Real-time data source for B3 assets.
- **Apache Kafka**: For asynchronous inter-service communication.
- **Schedule**: Library for periodic task orchestration.

## 🛠️ Environment Setup

### Environment Variables

Create a `.env` file in the root directory with the following settings:

```env
BRAPI_TOKEN=seu_token_aqui
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=market_data_db
```

### Installation

1. **Virtual Environment**:

```powershell
python -m venv venv
.\venv\Scripts\activate

```

2. **Dependencies**:

```powershell
pip install -r requirements.txt

```

## 🏃 Execution

To start the monitoring Worker:

```powershell
python main.py

```

The service is configured to update the full list every 30 minutes, adhering to the data update frequency and the Brapi free tier rate limits.

---

_This project is part of the My Broker B3 ecosystem for microservices architecture studies._
