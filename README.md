
# Inventory Data Engineering Pipeline

## 1. Project Overview

A Python-based data engineering pipeline that processes
inventory receipts, issues, transfers and adjustments
into daily inventory balances.

## 2. Business Objective

- Calculate daily inventory balances.
- Reconcile inventory movements.
- Handle backdated corrections.
- Identify invalid and duplicate records.
- Maintain pipeline execution history.

## 3. Technology Stack

- Python
- Pandas
- DuckDB
- Pytest
- SQL
- Parquet

## 4. Architecture

Source CSV
    |
Ingestion
    |
Data Validation
    |
Transformation
    |
Inventory Ledger
    |
Daily Balance Calculation
    |
DuckDB
    |
Reports and Reconciliation

## 5. Project Structure

See the repository directory structure.

## 6. Setup Instructions

python -m venv venv

Windows:
venv\Scripts\activate

pip install -r requirements.txt

## 7. Generate Sample Data

python scripts/generate_data.py --rows 500

## 8. Initialize Database

python -m src.database

## 9. Execute Pipeline

python -m src.pipeline

## 10. Export Reports

python -m src.export_reports

## 11. Run Tests

pytest -v

## 12. Data Quality

Documents duplicate handling, schema validation,
referential integrity and rejected records.

## 13. Idempotency and Backfills

Documents safe reruns and backdated corrections.

## 14. Performance

Documents benchmark results and optimization.

## 15. Limitations and Future Improvements

- Incremental balance recalculation.
- Cloud deployment.
- Scheduled orchestration.
- Advanced monitoring.