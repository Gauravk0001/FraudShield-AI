import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.ensemble import IsolationForest, RandomForestClassifier
try:
    import xgboost as xgb
    USE_XGB = True
except ImportError:
    USE_XGB = False
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

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

def generate_synthetic_fraud_dataset(n_samples=5000):
    np.random.seed(42)
    
    # 95% Normal, 5% Fraud
    n_fraud = int(n_samples * 0.05)
    n_normal = n_samples - n_fraud
    
    # Normal transactions
    normal_data = {
        "amount": np.random.exponential(scale=50.0, size=n_normal),
        "transaction_type_encoded": np.random.choice([0, 1, 2], size=n_normal, p=[0.7, 0.2, 0.1]),
        "hour_of_day": np.random.randint(8, 22, size=n_normal),
        "day_of_week": np.random.randint(0, 7, size=n_normal),
        "transaction_velocity_1h": np.random.poisson(lam=0.5, size=n_normal),
        "transaction_velocity_24h": np.random.poisson(lam=2.0, size=n_normal),
        "avg_amount_customer_30d": np.random.exponential(scale=60.0, size=n_normal) + 10.0,
        "time_since_last_transaction_seconds": np.random.exponential(scale=3600.0 * 12, size=n_normal) + 300,
        "is_new_device": np.random.choice([0, 1], size=n_normal, p=[0.92, 0.08]),
        "is_new_merchant": np.random.choice([0, 1], size=n_normal, p=[0.85, 0.15]),
        "location_changed": np.random.choice([0, 1], size=n_normal, p=[0.90, 0.10]),
        "is_fraud": 0
    }
    df_normal = pd.DataFrame(normal_data)
    df_normal["amount_deviation_ratio"] = df_normal["amount"] / (df_normal["avg_amount_customer_30d"] + 1.0)

    # Fraudulent transactions (high velocity, high amount, new device, late hours)
    fraud_data = {
        "amount": np.random.exponential(scale=450.0, size=n_fraud) + 200.0,
        "transaction_type_encoded": np.random.choice([0, 1, 2], size=n_fraud, p=[0.3, 0.5, 0.2]),
        "hour_of_day": np.random.choice([1, 2, 3, 4, 23], size=n_fraud),
        "day_of_week": np.random.randint(0, 7, size=n_fraud),
        "transaction_velocity_1h": np.random.poisson(lam=4.0, size=n_fraud) + 2,
        "transaction_velocity_24h": np.random.poisson(lam=12.0, size=n_fraud) + 5,
        "avg_amount_customer_30d": np.random.exponential(scale=40.0, size=n_fraud) + 5.0,
        "time_since_last_transaction_seconds": np.random.exponential(scale=60.0, size=n_fraud) + 5,
        "is_new_device": np.random.choice([0, 1], size=n_fraud, p=[0.20, 0.80]),
        "is_new_merchant": np.random.choice([0, 1], size=n_fraud, p=[0.25, 0.75]),
        "location_changed": np.random.choice([0, 1], size=n_fraud, p=[0.30, 0.70]),
        "is_fraud": 1
    }
    df_fraud = pd.DataFrame(fraud_data)
    df_fraud["amount_deviation_ratio"] = df_fraud["amount"] / (df_fraud["avg_amount_customer_30d"] + 1.0)

    df = pd.concat([df_normal, df_fraud], ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

def train_and_save_models():
    df = generate_synthetic_fraud_dataset(n_samples=5000)
    X = df[FEATURE_NAMES]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 1. Supervised Fraud Classifier (XGBoost / RandomForest)
    if USE_XGB:
        clf = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            eval_metric="logloss"
        )
        model_name = "XGBoost"
    else:
        clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        model_name = "RandomForest"

    clf.fit(X_train, y_train)

    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))

    # 2. Isolation Forest Anomaly Detector
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    # Train anomaly detector on normal samples
    iso_forest.fit(X_train[y_train == 0])

    # Save artifacts
    clf_path = os.path.join(ARTIFACTS_DIR, "fraud_classifier.joblib")
    iso_path = os.path.join(ARTIFACTS_DIR, "isolation_forest.joblib")
    meta_path = os.path.join(ARTIFACTS_DIR, "model_metadata.json")

    joblib.dump(clf, clf_path)
    joblib.dump(iso_forest, iso_path)

    metadata = {
        "version": "v1.0.0",
        "model_type": model_name,
        "feature_names": FEATURE_NAMES,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "roc_auc": roc_auc
        },
        "dataset": "Synthetic Financial Fraud Dataset (5,000 samples, 5% imbalance ratio)"
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print("Model training complete!")
    print(f"Model Type: {model_name}")
    print(f"Metrics: Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}, ROC-AUC={roc_auc:.4f}")
    print(f"Artifacts saved to {ARTIFACTS_DIR}")

if __name__ == "__main__":
    train_and_save_models()
