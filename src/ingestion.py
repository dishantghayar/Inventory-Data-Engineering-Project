
from pathlib import Path
import pandas as pd

def ingest_csv(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    df = pd.read_csv(
        file_path,
        dtype={
            "event_id": "string",
            "product_id": "string",
            "location_id": "string"
        }
    )

    df["source_file"] = file_path.name

    df["source_row"] = range(2, len(df) + 2)

    return df