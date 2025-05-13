import os
import numpy as np
from lightfm import LightFM
from sqlalchemy import create_engine, text
from scipy.sparse import coo_matrix

# Expect DATABASE_URL env var, e.g.:
# postgresql://recsys:recsys@db:5432/recsys
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

def load_interactions():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT user_id, item_id, rating FROM user_item_interactions"
        )).fetchall()
    return rows  # list of (user_id, item_id, rating)

def to_sparse_matrix(interactions):
    # Map raw IDs to contiguous indices
    users = sorted({u for u, _, _ in interactions})
    items = sorted({i for _, i, _ in interactions})
    u2idx = {u: idx for idx, u in enumerate(users)}
    i2idx = {i: idx for idx, i in enumerate(items)}
    data = np.array([r for _, _, r in interactions], dtype=np.float32)
    row  = np.array([u2idx[u] for u, _, _ in interactions], dtype=np.int32)
    col  = np.array([i2idx[i] for _, i, _ in interactions], dtype=np.int32)
    mat  = coo_matrix((data, (row, col)), shape=(len(users), len(items)))
    return mat, users, items

def save_embeddings(model, users, items):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        # wipe old embeddings
        conn.execute(text("TRUNCATE TABLE embeddings"))

        # user embeddings
        user_vecs = model.get_user_representations()[1]
        for uid, vec in zip(users, user_vecs):
            vec = [float(x) for x in vec]  # convert to float
            conn.execute(
                text("INSERT INTO embeddings(id, vector, type) VALUES (:id, :vec, 'user')"),
                {"id": uid, "vec": list(vec)}
            )

        # item embeddings
        item_vecs = model.get_item_representations()[1]
        for iid, vec in zip(items, item_vecs):
            vec = [float(x) for x in vec]  # convert to float
            conn.execute(
                text("INSERT INTO embeddings(id, vector, type) VALUES (:id, :vec, 'item')"),
                {"id": iid, "vec": list(vec)}
            )

def main():
    print("Loading interactions...")
    interactions = load_interactions()

    print(f"Converting {len(interactions)} interactions to sparse matrix...")
    mat, users, items = to_sparse_matrix(interactions)

    print("Training LightFM model...")
    model = LightFM(no_components=64, loss="warp")
    model.fit(mat, epochs=10, num_threads=4)

    print("Saving embeddings to database...")
    save_embeddings(model, users, items)

    print("✅ Training complete and embeddings stored.")

if __name__ == "__main__":
    main()
