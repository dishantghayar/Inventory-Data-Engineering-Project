
import pandas as pd
import pytest

from src.validation import validate_events


@pytest.fixture
def valid_event():
    return {
        "event_id": "EVT001",
        "product_id": "P001",
        "location_id": "WH001",
        "movement_type": "RECEIPT",
        "quantity": 10,
        "event_date": "2026-10-30",
    }


def test_missing_event_id(valid_event):
    valid_event["event_id"] = None
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_missing_product_id(valid_event):
    valid_event["product_id"] = None
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_missing_quantity(valid_event):
    valid_event["quantity"] = None
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_invalid_date(valid_event):
    valid_event["event_date"] = "not-a-date"
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_invalid_movement_type(valid_event):
    valid_event["movement_type"] = "UNKNOWN"
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_invalid_warehouse_id(valid_event):
    valid_event["location_id"] = "INVALID_WH"
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_negative_quantity(valid_event):
    valid_event["quantity"] = -10
    df = pd.DataFrame([valid_event])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1


def test_duplicate_event_id(valid_event):
    df = pd.DataFrame([valid_event, valid_event.copy()])

    accepted, rejected = validate_events(df)

    assert len(rejected) == 1