# Broker Market Data API

Microservico responsavel por alimentar o ecossistema **My Broker B3** com dados reais do mercado financeiro brasileiro. Busca cotacoes de ativos na API Brapi, persiste o historico no MongoDB e publica eventos em um topico Kafka para os servicos consumidores.

> Este servico faz parte de uma serie de artigos documentando o ecossistema **My Broker B3**.
> Acompanhe a serie completa em [dev.to/rvneto](https://dev.to/rvneto).

---

## Arquitetura e Fluxo

```
[Brapi API] ---> [broker-market-data-api] ---> [MongoDB: price_history]
                         |
                         +---> [Kafka: trading-assets-market-data-v1]
                                        |
                              [broker-asset-api] (consumer)
```

1. **Ingestao**: Worker itera uma watchlist de 50 ativos (Blue Chips, FIIs, ETFs)
2. **Busca**: Requisicoes individuais a API Brapi respeitando o rate limit do plano gratuito
3. **Persistencia**: Payload completo armazenado no MongoDB para analise historica e auditoria
4. **Streaming**: Eventos de preco publicados no Kafka para os consumidores downstream
5. **Agendamento**: Executa a cada 30 minutos (configuravel), roda imediatamente ao iniciar

---

## Stack Tecnologica

| Tecnologia | Uso |
| :--- | :--- |
| **Python 3.12+** | Runtime do servico |
| **MongoDB** | Persistencia historica de precos |
| **Apache Kafka** (confluent-kafka) | Streaming assincrono de eventos |
| **Brapi API** | Fonte de dados reais da B3 |
| **Schedule** | Orquestracao de tarefas periodicas |

---

## Payload Kafka

**Topico:** `trading-assets-market-data-v1`
**Key:** simbolo do ativo (ex: `PETR4`)

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

## Variaveis de Ambiente

| Variavel | Descricao | Padrao |
| :--- | :--- | :--- |
| **BRAPI_TOKEN** | Token da API Brapi (obrigatorio) | — |
| **MONGO_HOST** | Host do MongoDB | localhost |
| **MONGO_PORT** | Porta do MongoDB | 27017 |
| **MONGO_DB** | Nome do banco MongoDB | market_data_db |
| **KAFKA_BOOTSTRAP_SERVERS** | Endereco do broker Kafka | localhost:9092 |
| **KAFKA_TOPIC** | Topico Kafka para publicacao | trading-assets-market-data-v1 |
| **SYNC_INTERVAL_MINUTES** | Intervalo de sincronizacao em minutos | 30 |

> **BRAPI_TOKEN** nao possui valor padrao e deve ser fornecido explicitamente.

---

## Configuracao Local

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # preencha seu BRAPI_TOKEN
python main.py
```

## Rodando com Docker

```bash
docker build -t broker-market-data-api .
```

```bash
docker run \
  -e BRAPI_TOKEN=seu_token_aqui \
  -e MONGO_HOST=broker-market-data-db \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  broker-market-data-api
```

---

*Este projeto faz parte do ecossistema My Broker B3 para estudos de arquitetura de microservicos.*
