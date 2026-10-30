
from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "data" / "inventory.duckdb"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def initialize_database():
    con = get_connection()

    con.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR PRIMARY KEY,
            product_name VARCHAR NOT NULL,
            category VARCHAR NOT NULL
        );

        CREATE TABLE IF NOT EXISTS locations (
            location_id VARCHAR PRIMARY KEY,
            location_name VARCHAR NOT NULL,
            location_type VARCHAR NOT NULL
        );

        CREATE TABLE IF NOT EXISTS inventory_events (
            event_id VARCHAR PRIMARY KEY,
            event_date DATE NOT NULL,
            event_timestamp TIMESTAMP,
            product_id VARCHAR NOT NULL,
            movement_type VARCHAR NOT NULL,
            quantity DECIMAL(18, 3) NOT NULL,
            adjustment_direction VARCHAR,
            source_location_id VARCHAR,
            destination_location_id VARCHAR,
            source_file VARCHAR NOT NULL,
            run_id VARCHAR NOT NULL
        );

        CREATE TABLE IF NOT EXISTS inventory_ledger (
            ledger_id VARCHAR PRIMARY KEY,
            event_id VARCHAR NOT NULL,
            event_date DATE NOT NULL,
            product_id VARCHAR NOT NULL,
            location_id VARCHAR NOT NULL,
            movement_type VARCHAR NOT NULL,
            quantity_delta DECIMAL(18, 3) NOT NULL,
            run_id VARCHAR NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_inventory_balances (
            inventory_date DATE NOT NULL,
            product_id VARCHAR NOT NULL,
            location_id VARCHAR NOT NULL,
            opening_quantity DECIMAL(18, 3) NOT NULL,
            net_movement DECIMAL(18, 3) NOT NULL,
            closing_quantity DECIMAL(18, 3) NOT NULL,
            PRIMARY KEY (
                inventory_date, product_id, location_id
            )
        );

        CREATE TABLE IF NOT EXISTS rejected_records (
            reject_id VARCHAR PRIMARY KEY,
            event_id VARCHAR,
            source_file VARCHAR NOT NULL,
            source_row INTEGER NOT NULL,
            raw_record VARCHAR NOT NULL,
            rejection_reason VARCHAR NOT NULL,
            run_id VARCHAR NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id VARCHAR PRIMARY KEY,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            status VARCHAR NOT NULL,
            input_count INTEGER DEFAULT 0,
            accepted_count INTEGER DEFAULT 0,
            rejected_count INTEGER DEFAULT 0,
            duplicate_count INTEGER DEFAULT 0,
            failure_reason VARCHAR
        );
    """)

    con.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
    


def rebuild_balances(con):
    con.execute("DELETE FROM daily_inventory_balances")

    con.execute("""
        INSERT INTO daily_inventory_balances
        WITH daily AS (
            SELECT
                event_date,
                product_id,
                location_id,
                SUM(quantity_delta) AS net_movement
            FROM inventory_ledger
            GROUP BY 1, 2, 3
        ),
        calculated AS (
            SELECT
                event_date,
                product_id,
                location_id,
                net_movement,
                SUM(net_movement) OVER (
                    PARTITION BY product_id, location_id
                    ORDER BY event_date
                    ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ) AS closing_quantity
            FROM daily
        )
        SELECT
            event_date,
            product_id,
            location_id,
            closing_quantity - net_movement,
            net_movement,
            closing_quantity
        FROM calculated
    """)
    

import pandas as pd
from pathlib import Path

def load_master_data():
    con = get_connection()

    base = Path(__file__).resolve().parents[1]

    products = pd.read_csv(
        base / "data/sample/products.csv"
    )

    locations = pd.read_csv(
        base / "data/sample/locations.csv"
    )

    con.register("products_df", products)
    con.register("locations_df", locations)

    con.execute("""
        INSERT INTO products
        SELECT * FROM products_df
        ON CONFLICT (product_id) DO NOTHING
    """)

    con.execute("""
        INSERT INTO locations
        SELECT * FROM locations_df
        ON CONFLICT (location_id) DO NOTHING
    """)

    con.close()

    print("Master data loaded successfully.")