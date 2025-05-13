import os
import pandas as pd
from sqlalchemy import create_engine, text

# Config via env vars
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://recsys:recsys@db:5432/recsys")
CSV_PATH     = os.getenv("CSV_PATH", "/data/amazon_ratings_beauty.csv")
BATCH_SIZE   = int(os.getenv("BATCH_SIZE", 1000))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_last_offset():
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT last_offset
              FROM stream_metadata
             WHERE stream_name = 'beauty_ratings'
        """)).fetchone()
    return row[0] if row else 0

def update_offset(new_offset):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO stream_metadata(stream_name, last_offset)
            VALUES ('beauty_ratings', :off)
            ON CONFLICT (stream_name)
              DO UPDATE SET last_offset = :off
        """), {"off": new_offset})

def stream_batch():
    offset = get_last_offset()

    # Read next batch; do NOT auto-parse dates here
    df = pd.read_csv(
        CSV_PATH,
        skiprows=offset + 1,
        nrows=BATCH_SIZE,
        names=["user_id", "item_id", "rating", "ts"],
        dtype={"user_id": str, "item_id": str, "rating": float},
        header=None,
    )

    if df.empty:
        print("✅ No new records to stream.")
        return

    # Convert epoch seconds string/number -> real TIMESTAMP
    df["ts"] = pd.to_datetime(df["ts"], unit="s")

    # Append to Postgres
    df.to_sql(
        "user_item_interactions",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500
    )

    new_offset = offset + len(df)
    update_offset(new_offset)
    print(f"Streamed {len(df)} records (offset {offset} → {new_offset}).")

if __name__ == "__main__":
    stream_batch()
