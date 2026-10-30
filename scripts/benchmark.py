
import time
from pathlib import Path

from src.ingestion import ingest_csv

file_path = Path(
    "data/sample/inventory_movements.csv"
)

start = time.perf_counter()

df = ingest_csv(file_path)

elapsed = time.perf_counter() - start

print("Records processed:", len(df))
print("Execution time:", round(elapsed, 4), "seconds")

if elapsed > 0:
    print(
        "Records per second:",
        round(len(df) / elapsed, 2)
    )