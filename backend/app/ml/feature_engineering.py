import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction
from app.models.entities import Customer, Merchant, Device

FEATURE_NAMES = [
    "amount",
    "transaction_type_encoded",
    "hour_of_day",
    "day_of_week",
    "transaction_velocity_1h",
    "transaction_velocity_24h",
    "avg_amount_customer_30d",
    "amount_deviation_ratio",
    "time_since_last_transaction_seconds",
    "is_new_device",
    "is_new_merchant",
    "location_changed"
]

TRANSACTION_TYPE_MAP = {
    "CARD_PRESENT": 0,
    "CARD_NOT_PRESENT": 1,
    "ONLINE_PAYMENT": 1,
    "WIRE_TRANSFER": 2,
    "ATM_WITHDRAWAL": 2
}

def extract_features(
    db: Session,
    transaction_data: Dict[str, Any]
) -> Dict[str, float]:
    tx_timestamp = transaction_data.get("timestamp")
    if isinstance(tx_timestamp, str):
        tx_timestamp = datetime.fromisoformat(tx_timestamp.replace('Z', '+00:00'))
    elif tx_timestamp is None:
        tx_timestamp = datetime.now(timezone.utc)

    customer_id = str(transaction_data["customer_id"])
    merchant_id = str(transaction_data["merchant_id"])
    device_id = str(transaction_data["device_id"])
    amount = float(transaction_data["amount"])
    tx_type_str = str(transaction_data.get("transaction_type", "CARD_NOT_PRESENT")).upper()
    location = str(transaction_data.get("location", ""))

    # Historical queries for customer
    one_hour_ago = tx_timestamp - timedelta(hours=1)
    twenty_four_hours_ago = tx_timestamp - timedelta(hours=24)
    thirty_days_ago = tx_timestamp - timedelta(days=30)

    # 1. Transaction velocities
    velocity_1h = db.query(func.count(Transaction.id)).filter(
        Transaction.customer_id == customer_id,
        Transaction.timestamp >= one_hour_ago,
        Transaction.timestamp <= tx_timestamp
    ).scalar() or 0

    velocity_24h = db.query(func.count(Transaction.id)).filter(
        Transaction.customer_id == customer_id,
        Transaction.timestamp >= twenty_four_hours_ago,
        Transaction.timestamp <= tx_timestamp
    ).scalar() or 0

    # 2. Avg amount last 30d
    avg_30d = db.query(func.avg(Transaction.amount)).filter(
        Transaction.customer_id == customer_id,
        Transaction.timestamp >= thirty_days_ago,
        Transaction.timestamp <= tx_timestamp
    ).scalar() or amount

    amount_dev_ratio = amount / (avg_30d + 1.0)

    # 3. Time since last transaction
    last_tx = db.query(Transaction).filter(
        Transaction.customer_id == customer_id,
        Transaction.timestamp < tx_timestamp
    ).order_by(Transaction.timestamp.desc()).first()

    if last_tx and last_tx.timestamp:
        last_time = last_tx.timestamp
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        curr_time = tx_timestamp if tx_timestamp.tzinfo else tx_timestamp.replace(tzinfo=timezone.utc)
        time_diff = (curr_time - last_time).total_seconds()
        location_changed = 1.0 if (last_tx.location and last_tx.location != location) else 0.0
    else:
        time_diff = 86400.0 # 24 hours default
        location_changed = 0.0

    # 4. Device and Merchant novelty
    device_seen = db.query(Transaction).filter(
        Transaction.customer_id == customer_id,
        Transaction.device_id == device_id
    ).first() is not None

    merchant_seen = db.query(Transaction).filter(
        Transaction.customer_id == customer_id,
        Transaction.merchant_id == merchant_id
    ).first() is not None

    features = {
        "amount": amount,
        "transaction_type_encoded": float(TRANSACTION_TYPE_MAP.get(tx_type_str, 1)),
        "hour_of_day": float(tx_timestamp.hour),
        "day_of_week": float(tx_timestamp.weekday()),
        "transaction_velocity_1h": float(velocity_1h),
        "transaction_velocity_24h": float(velocity_24h),
        "avg_amount_customer_30d": float(avg_30d),
        "amount_deviation_ratio": float(amount_dev_ratio),
        "time_since_last_transaction_seconds": float(time_diff),
        "is_new_device": 0.0 if device_seen else 1.0,
        "is_new_merchant": 0.0 if merchant_seen else 1.0,
        "location_changed": float(location_changed)
    }

    return features
