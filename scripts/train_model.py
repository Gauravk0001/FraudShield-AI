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

    # Fraudulent transactions across realistic topologies:
    # 1. Large Wire / Account Takeover (single large amount, novel device, foreign location)
    # 2. High Velocity / Automated Card Testing (burst velocity, short intervals)
    # 3. Mixed Multi-Vector Fraud
    n_fraud_large = int(n_fraud * 0.45)
    n_fraud_velocity = int(n_fraud * 0.35)
    n_fraud_mixed = n_fraud - n_fraud_large - n_fraud_velocity

    fraud_dfs = []

    # Topology 1: Large Wire / Account Takeover
    df_large = pd.DataFrame({
        "amount": np.random.uniform(2500.0, 18000.0, size=n_fraud_large),
        "transaction_type_encoded": np.random.choice([1, 2], size=n_fraud_large, p=[0.3, 0.7]),
        "hour_of_day": np.random.choice([0, 1, 2, 3, 4, 22, 23], size=n_fraud_large),
        "day_of_week": np.random.randint(0, 7, size=n_fraud_large),
        "transaction_velocity_1h": np.random.poisson(lam=0.5, size=n_fraud_large),
        "transaction_velocity_24h": np.random.poisson(lam=1.5, size=n_fraud_large),
        "avg_amount_customer_30d": np.random.uniform(40.0, 120.0, size=n_fraud_large),
        "time_since_last_transaction_seconds": np.random.exponential(scale=3600.0 * 24, size=n_fraud_large) + 3600,
        "is_new_device": np.ones(n_fraud_large),
        "is_new_merchant": np.random.choice([0, 1], size=n_fraud_large, p=[0.1, 0.9]),
        "location_changed": np.random.choice([0, 1], size=n_fraud_large, p=[0.1, 0.9]),
        "is_fraud": 1
    })
    df_large["amount_deviation_ratio"] = df_large["amount"] / (df_large["avg_amount_customer_30d"] + 1.0)
    fraud_dfs.append(df_large)

    # Topology 2: Velocity / Card Testing
    df_velo = pd.DataFrame({
        "amount": np.random.uniform(15.0, 350.0, size=n_fraud_velocity),
        "transaction_type_encoded": np.random.choice([0, 1], size=n_fraud_velocity, p=[0.2, 0.8]),
        "hour_of_day": np.random.randint(0, 24, size=n_fraud_velocity),
        "day_of_week": np.random.randint(0, 7, size=n_fraud_velocity),
        "transaction_velocity_1h": np.random.poisson(lam=5.0, size=n_fraud_velocity) + 3,
        "transaction_velocity_24h": np.random.poisson(lam=15.0, size=n_fraud_velocity) + 8,
        "avg_amount_customer_30d": np.random.uniform(30.0, 80.0, size=n_fraud_velocity),
        "time_since_last_transaction_seconds": np.random.exponential(scale=45.0, size=n_fraud_velocity) + 5,
        "is_new_device": np.random.choice([0, 1], size=n_fraud_velocity, p=[0.3, 0.7]),
        "is_new_merchant": np.random.choice([0, 1], size=n_fraud_velocity, p=[0.2, 0.8]),
        "location_changed": np.random.choice([0, 1], size=n_fraud_velocity, p=[0.4, 0.6]),
        "is_fraud": 1
    })
    df_velo["amount_deviation_ratio"] = df_velo["amount"] / (df_velo["avg_amount_customer_30d"] + 1.0)
    fraud_dfs.append(df_velo)

    # Topology 3: Mixed High Velocity & High Amount
    df_mixed = pd.DataFrame({
        "amount": np.random.uniform(1500.0, 8000.0, size=n_fraud_mixed),
        "transaction_type_encoded": np.random.choice([1, 2], size=n_fraud_mixed, p=[0.4, 0.6]),
        "hour_of_day": np.random.choice([1, 2, 3, 4, 23], size=n_fraud_mixed),
        "day_of_week": np.random.randint(0, 7, size=n_fraud_mixed),
        "transaction_velocity_1h": np.random.poisson(lam=3.0, size=n_fraud_mixed) + 2,
        "transaction_velocity_24h": np.random.poisson(lam=8.0, size=n_fraud_mixed) + 4,
        "avg_amount_customer_30d": np.random.uniform(50.0, 100.0, size=n_fraud_mixed),
        "time_since_last_transaction_seconds": np.random.exponential(scale=120.0, size=n_fraud_mixed) + 10,
        "is_new_device": np.ones(n_fraud_mixed),
        "is_new_merchant": np.ones(n_fraud_mixed),
        "location_changed": np.ones(n_fraud_mixed),
        "is_fraud": 1
    })
    df_mixed["amount_deviation_ratio"] = df_mixed["amount"] / (df_mixed["avg_amount_customer_30d"] + 1.0)
    fraud_dfs.append(df_mixed)

    df_fraud = pd.concat(fraud_dfs, ignore_index=True)
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
