
import uuid
import logging
import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.database import (
    get_connection,
    initialize_database,
    rebuild_balances
)
from src.ingestion import ingest_csv
from src.validation import validate_movements
from src.transformation import transform_movements
from src.publishing import publish_events
from src.ledger_publishing import publish_ledger
from src.logging_config import setup_logging

BASE_DIR = Path(__file__).resolve().parents[1]

def run_pipeline(input_file):
    logger = setup_logging()
    run_id = str(uuid.uuid4())

    start_time = datetime.now()

    con = get_connection()

    input_count = 0
    accepted_count = 0
    rejected_count = 0
    duplicate_count = 0

    con.execute("""
        INSERT INTO pipeline_runs (
            run_id, start_time, status
        )
        VALUES (?, ?, 'RUNNING')
    """, [run_id, start_time])

    try:
        logger.info("Pipeline started: %s", run_id)

        df = ingest_csv(input_file)
        input_count = len(df)

        products = con.execute(
            "SELECT * FROM products"
        ).df()

        locations = con.execute(
            "SELECT * FROM locations"
        ).df()

        accepted, rejected = validate_movements(
            df, products, locations
        )

        rejected_count = len(rejected)

        ledger = transform_movements(accepted)

        con.execute("BEGIN TRANSACTION")

        inserted, duplicate_count = publish_events(
            con, accepted, run_id
        )

        # Only publish ledger rows for newly inserted events.
        if inserted:
            new_events = con.execute(
                """
                SELECT *
                FROM inventory_events
                WHERE run_id = ?
                """,
                [run_id]
            ).df()

            new_ledger = transform_movements(
                new_events
            )

            publish_ledger(
                con, new_ledger, run_id
            )

        # Save rejects for audit.
        for _, row in rejected.iterrows():
            con.execute(
                """
                INSERT INTO rejected_records
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    str(uuid.uuid4()),
                    row.get("event_id"),
                    str(row.get("source_file")),
                    int(row.get("source_row") or 0),
                    str(row.get("raw_record")),
                    row.get("rejection_reason"),
                    run_id
                ]
            )

        rebuild_balances(con)

        accepted_count = inserted

        con.execute("""
            UPDATE pipeline_runs
            SET
                end_time = ?,
                status = 'SUCCESS',
                input_count = ?,
                accepted_count = ?,
                rejected_count = ?,
                duplicate_count = ?
            WHERE run_id = ?
        """, [
            datetime.now(),
            input_count,
            accepted_count,
            rejected_count,
            duplicate_count,
            run_id
        ])

        con.execute("COMMIT")

        logger.info("Pipeline completed: %s", run_id)
        logger.info("Input rows: %s", input_count)
        logger.info("Accepted rows: %s", accepted_count)
        logger.info("Rejected rows: %s", rejected_count)
        logger.info("Duplicates: %s", duplicate_count)

    except Exception as exc:
        con.execute("ROLLBACK")

        con.execute("""
            UPDATE pipeline_runs
            SET
                end_time = ?,
                status = 'FAILED',
                failure_reason = ?
            WHERE run_id = ?
        """, [
            datetime.now(),
            str(exc),
            run_id
        ])

        logger.exception("Pipeline failed")
        raise

    finally:
        con.close()

    return run_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="data/sample/inventory_movements.csv"
    )

    args = parser.parse_args()

    initialize_database()

    run_pipeline(BASE_DIR / args.input)