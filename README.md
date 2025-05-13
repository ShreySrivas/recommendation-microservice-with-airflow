# Recommendation Service with Airflow & Docker

A reproducible, containerized recommendation engine that:

* **Streams** Amazon Beauty Ratings data into Postgres in micro-batches
* **Trains** a LightFM model and stores collaborative-filtering embeddings
* **Serves** real-time recommendations via a FastAPI endpoint
* **Orchestrates** data streaming and model retraining with Apache Airflow

---

## 🏗 Architecture

```
CSV ──▶ Stream (simulate_stream.py) ──▶ Postgres ──┐
│                                                │
▼                                                ▼
Trainer (train.py) ──▶ Postgres                   │
│                                                │
▼                                                │
API (FastAPI) ◀──────── Embeddings & Interactions ┘

Airflow DAG: stream_data ▶ retrain_model (every 5 minutes)
```

---

## 🚀 Prerequisites

* Docker Engine & Docker Compose V2
* (Optional) Python 3.10 for local scripts

---

## 🔧 Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/you/RecommendationServicewithAirflow.git
   cd RecommendationServicewithAirflow
   ```

2. **Create & edit** your `.env` (see `.env.example`):

   ```ini
   DATABASE_URL=postgresql://recsys:recsys@db:5432/recsys
   CSV_PATH=/data/amazon_ratings_beauty.csv
   HOST_DATA_DIR=/absolute/path/to/recsys/data
   BATCH_SIZE=1000
   ```

3. **Download** the Kaggle dataset and place it in:

   ```
   ./data/amazon_ratings_beauty.csv
   ```

---

## ▶️ Running Locally

1. **Start core services** (DB, API, Stream):

   ```bash
   docker compose up --build -d db api stream
   ```

2. **Build the trainer image**:

   ```bash
   docker compose build trainer
   ```

3. **Launch Airflow** (scheduler + webserver):

   ```bash
   docker compose up -d airflow
   ```

4. **Unpause & trigger** the DAG:

   ```bash
   docker compose exec airflow \
     airflow dags unpause retrain_and_stream
   docker compose exec airflow \
     airflow dags trigger retrain_and_stream
   ```

5. **Monitor** via logs or the Airflow UI at [http://localhost:8080](http://localhost:8080).

---

## ✔️ Verification

Check that data is flowing and embeddings are generated:

```bash
# Interaction count
docker compose exec db \
  psql -U recsys -d recsys -c "SELECT count(*) FROM user_item_interactions;"

# Embedding count
docker compose exec db \
  psql -U recsys -d recsys -c "SELECT count(*) FROM embeddings;"
```

---

## 📁 Project Structure

```text
.
├── api/             # FastAPI service for recommendations
├── data/            # CSV dataset (amazon_ratings_beauty.csv)
├── stream/          # simulate_stream.py & Dockerfile
├── training/        # train.py, model code & Dockerfile
├── airflow/         # DAGs, Dockerfile, Airflow configs
├── docker-compose.yml
└── README.md
```

---

## 📄 License

[MIT](LICENSE)
