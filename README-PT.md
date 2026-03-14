# Broker Market Data API 📈

Este microserviço é o componente responsável por alimentar o ecossistema do projeto **My Broker B3** com dados reais do mercado financeiro brasileiro. Ele atua como um ingestor que consome informações da API externa Brapi e as distribui para persistência histórica e publicação dos preços em tópico Kafka para atualização das bases.

## 🏗️ Arquitetura e Fluxo

Conforme o desenho técnico do sistema, este serviço realiza o seguinte fluxo de dados:

1.  **Ingestão**: O Worker percorre uma Watchlist de 50 ativos (Blue Chips, FIIs e ETFs).
2.  **Consumo**: Realiza requisições individuais à API Brapi, respeitando o limite de um ativo por chamada do plano gratuito.
3.  **Persistência Histórica**: Armazena o payload completo no **MongoDB** (`broker_market_data_db`) para futuras análises e auditoria.
4.  **Publicação em Tópico Kafka**: Publica mensagens com as informações atualizadas dos preços no tópico `trading-assets-market-data-v1` que depois serão consumidas pelos demais serviços.

## 🚀 Tecnologias

- **Python 3.12+**
- **MongoDB**: Banco orientado a documentos para histórico de preços.
- **Brapi API**: Fonte de dados real-time para ativos da B3.
- **Apache Kafka**: Para comunicação assíncrona entre serviços.
- **Schedule**: Biblioteca para orquestração de tarefas periódicas.

## 🛠️ Configuração do Ambiente

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do diretório com as seguintes configurações:

```env
BRAPI_TOKEN=seu_token_aqui
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=market_data_db
```

### Instalação

1. **Ambiente Virtual**:

```powershell
python -m venv venv
.\venv\Scripts\activate

```

2. **Dependências**:

```powershell
pip install -r requirements.txt

```

## 🏃 Execução

Para iniciar o Worker de monitoramento:

```powershell
python main.py

```

O serviço está configurado para atualizar a lista completa a cada **30 minutos**, respeitando a frequência de atualização dos dados e os limites de requisições do plano gratuito da Brapi.

## 📊 Estrutura do Cache (Redis)

Os dados são disponibilizados para os outros microserviços do ecossistema no seguinte formato:

- **Padrão da Chave**: `ticker:price:{SYMBOL}` (ex: `ticker:price:PETR4`)
- **Tipo de Dado**: `HASH`
- **Campos**: `symbol`, `price`, `volume`, `timestamp`, `created_at`.

---

_Este projeto faz parte do ecossistema My Broker B3 para estudos de arquitetura de microserviços._
