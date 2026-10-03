"""
FraudShield AI — Canonical Feature Schema Definition Layer

Provides authoritative feature definitions, column orderings, data types,
and validation utilities shared across offline training, batch evaluation,
and real-time online serving.

Guarantees:
1. Exact feature parity between training and serving.
2. Automated rejection of label leakage ('isFraud', 'isFlaggedFraud').
3. Explicit classification of balance-derived synthetic shortcuts.
"""

from typing import List, Dict, Any, Optional
import json

SCHEMA_VERSION = "2.1.0"

# Label columns strictly prohibited from entering feature sets
FORBIDDEN_LABEL_COLUMNS = {
    "isfraud",
    "isflaggedfraud",
    "is_fraud",
    "is_flagged_fraud",
    "fraud_label",
    "ground_truth",
    "label"
}

# Transaction type mapping for categorical encoding
PAYSIM_TYPE_MAP: Dict[str, int] = {
    "PAYMENT": 0,
    "CASH_IN": 1,
    "DEBIT": 2,
    "CASH_OUT": 3,
    "TRANSFER": 4
}

# 1. PaySim Feature Set WITHOUT balance-derived shortcuts (Defensible Baseline)
PAYSIM_FEATURES_NO_BALANCE: List[str] = [
    "amount",
    "log_amount",
    "type_encoded",
    "step_hour_of_day",
    "step_day_of_week",
    "velocity_origin_1h",
    "velocity_origin_6h",
    "velocity_origin_24h",
    "total_amount_origin_1h",
    "total_amount_origin_6h",
    "total_amount_origin_24h",
    "historical_avg_amount_origin",
    "amount_deviation_ratio",
    "is_first_time_destination",
    "dest_prior_inbound_count",
    "is_dest_customer_p2p"
]

# 2. PaySim Feature Set WITH balance-derived shortcuts (Exploratory Prototype Only)
PAYSIM_FEATURES_WITH_BALANCE: List[str] = PAYSIM_FEATURES_NO_BALANCE + [
    "origin_balance_discrepancy",
    "dest_balance_discrepancy",
    "amount_to_origin_balance_ratio",
    "account_emptied_indicator",
    "oldbalance_org",
    "newbalance_orig"
]

# 3. Native FraudShield Feature Set (for backward-compatible non-PaySim scoring)
NATIVE_FEATURE_NAMES: List[str] = [
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

FEATURE_METADATA: Dict[str, Dict[str, Any]] = {
    "amount": {
        "type": "float",
        "is_balance_derived": False,
        "description": "Raw transaction monetary amount"
    },
    "log_amount": {
        "type": "float",
        "is_balance_derived": False,
        "description": "log1p(amount) for scale normalization"
    },
    "type_encoded": {
        "type": "int",
        "is_balance_derived": False,
        "description": "Ordinal encoding of transaction type (PAYMENT=0, CASH_IN=1, DEBIT=2, CASH_OUT=3, TRANSFER=4)"
    },
    "step_hour_of_day": {
        "type": "int",
        "is_balance_derived": False,
        "description": "Simulated step modulo 24 (hourly cycle)"
    },
    "step_day_of_week": {
        "type": "int",
        "is_balance_derived": False,
        "description": "(Simulated step // 24) modulo 7 (day cycle)"
    },
    "velocity_origin_1h": {
        "type": "int",
        "is_balance_derived": False,
        "description": "Number of transactions by origin account in strictly prior 1 simulated step"
    },
    "velocity_origin_6h": {
        "type": "int",
        "is_balance_derived": False,
        "description": "Number of transactions by origin account in strictly prior 6 simulated steps"
    },
    "velocity_origin_24h": {
        "type": "int",
        "is_balance_derived": False,
        "description": "Number of transactions by origin account in strictly prior 24 simulated steps"
    },
    "total_amount_origin_1h": {
        "type": "float",
        "is_balance_derived": False,
        "description": "Sum of transaction amounts by origin account in strictly prior 1 simulated step"
    },
    "total_amount_origin_6h": {
        "type": "float",
        "is_balance_derived": False,
        "description": "Sum of transaction amounts by origin account in strictly prior 6 simulated steps"
    },
    "total_amount_origin_24h": {
        "type": "float",
        "is_balance_derived": False,
        "description": "Sum of transaction amounts by origin account in strictly prior 24 simulated steps"
    },
    "historical_avg_amount_origin": {
        "type": "float",
        "is_balance_derived": False,
        "description": "Running average transaction amount for origin account prior to current event"
    },
    "amount_deviation_ratio": {
        "type": "float",
        "is_balance_derived": False,
        "description": "Ratio of current transaction amount to historical origin average"
    },
    "is_first_time_destination": {
        "type": "float",
        "is_balance_derived": False,
        "description": "1.0 if origin has never transacted with destination prior to this event, else 0.0"
    },
    "dest_prior_inbound_count": {
        "type": "int",
        "is_balance_derived": False,
        "description": "Number of prior inbound transfers received by destination account"
    },
    "is_dest_customer_p2p": {
        "type": "float",
        "is_balance_derived": False,
        "description": "1.0 if destination account starts with 'C' (P2P), 0.0 if starts with 'M' (Merchant)"
    },
    "origin_balance_discrepancy": {
        "type": "float",
        "is_balance_derived": True,
        "description": "newbalanceOrig + amount - oldbalanceOrg (PaySim synthetic shortcut variable)"
    },
    "dest_balance_discrepancy": {
        "type": "float",
        "is_balance_derived": True,
        "description": "oldbalanceDest + amount - newbalanceDest (PaySim synthetic shortcut variable)"
    },
    "amount_to_origin_balance_ratio": {
        "type": "float",
        "is_balance_derived": True,
        "description": "amount / (oldbalanceOrg + 1.0) (PaySim synthetic shortcut variable)"
    },
    "account_emptied_indicator": {
        "type": "float",
        "is_balance_derived": True,
        "description": "1.0 if oldbalanceOrg > 0 and newbalanceOrig == 0, else 0.0 (PaySim shortcut)"
    },
    "oldbalance_org": {
        "type": "float",
        "is_balance_derived": True,
        "description": "Origin initial balance"
    },
    "newbalance_orig": {
        "type": "float",
        "is_balance_derived": True,
        "description": "Origin post-transaction balance"
    }
}

def validate_feature_columns(columns: List[str]) -> None:
    """
    Enforces zero label leakage by ensuring forbidden ground-truth labels
    never appear in any feature column list.
    """
    for col in columns:
        normalized = col.lower().strip()
        if normalized in FORBIDDEN_LABEL_COLUMNS:
            raise ValueError(
                f"FATAL DATA LEAKAGE DETECTED: Ground-truth label '{col}' found in feature list! "
                f"Ground-truth labels must NEVER be used as model inputs or online scoring features."
            )

def get_feature_schema(with_balance: bool = False) -> Dict[str, Any]:
    """Generates the authoritative JSON-serializable feature schema."""
    features = PAYSIM_FEATURES_WITH_BALANCE if with_balance else PAYSIM_FEATURES_NO_BALANCE
    validate_feature_columns(features)
    return {
        "schema_version": SCHEMA_VERSION,
        "variant": "with_balance" if with_balance else "no_balance",
        "features_count": len(features),
        "features": features,
        "is_synthetic_shortcut_enabled": with_balance,
        "metadata": {f: FEATURE_METADATA.get(f, {}) for f in features}
    }

def export_feature_schema(output_path: str, with_balance: bool = False) -> None:
    """Exports the canonical feature schema to JSON."""
    schema = get_feature_schema(with_balance=with_balance)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
