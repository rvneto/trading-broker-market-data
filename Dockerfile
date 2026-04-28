FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY main.py .

# Environment variables with safe defaults (override via docker-compose or -e flags)
ENV MONGO_HOST=localhost \
    MONGO_PORT=27017 \
    MONGO_DB=market_data_db \
    KAFKA_BOOTSTRAP_SERVERS=localhost:9092 \
    KAFKA_TOPIC=trading-assets-market-data-v1 \
    SYNC_INTERVAL_MINUTES=30

# BRAPI_TOKEN must be provided at runtime -- no default to avoid accidental exposure
# docker run -e BRAPI_TOKEN=your_token_here ...

CMD ["python", "main.py"]
