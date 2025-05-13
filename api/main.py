import os
import logging
import numpy as np
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from scipy.spatial.distance import cdist

app = FastAPI(title="Recsys API")

# Configure logger (uses Uvicorn’s logger under the hood)
logger = logging.getLogger("uvicorn.error")

# Must be set in your .env / env_file
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# In-memory maps: text user_id → embedding vector
user_emb: dict[str, np.ndarray] = {}
item_emb: dict[str, np.ndarray] = {}

@app.on_event("startup")
def load_embeddings():
    global user_emb, item_emb
    with engine.connect() as conn:
        # Load user embeddings (IDs are now text/varchar)
        rows = conn.execute(text("""
            SELECT id, vector
              FROM embeddings
             WHERE type = 'user'
        """)).all()
        user_emb = {str(r.id): np.array(r.vector) for r in rows}

        # Load item embeddings
        rows = conn.execute(text("""
            SELECT id, vector
              FROM embeddings
             WHERE type = 'item'
        """)).all()
        item_emb = {str(r.id): np.array(r.vector) for r in rows}

    logger.info(f"Loaded {len(user_emb)} user embeddings and {len(item_emb)} item embeddings")

@app.get("/recommend/{user_id}/{k}")
def recommend(user_id: str, k: int = 10):
    # user_id is now a string
    if user_id not in user_emb:
        raise HTTPException(status_code=404, detail="User not found")

    u_vec = user_emb[user_id].reshape(1, -1)
    all_ids = list(item_emb.keys())
    item_matrix = np.vstack([item_emb[i] for i in all_ids])

    sims = 1 - cdist(u_vec, item_matrix, metric="cosine").flatten()
    top_idx = np.argsort(-sims)[:k]

    recs = [
        {"item_id": all_ids[i], "score": float(sims[i])}
        for i in top_idx
    ]
    return {"user_id": user_id, "recommendations": recs}
