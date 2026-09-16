import os
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd

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

TX_TYPE_MAP = {
    "CARD_PRESENT": 0,
    "CARD_NOT_PRESENT": 1,
    "ONLINE_PAYMENT": 1,
    "WIRE_TRANSFER": 2,
    "ATM_WITHDRAWAL": 2
}

class CausalEntityTracker:
    """
    Maintains chronological historical state for customers, merchants, and devices.
    Guarantees strict causal ordering: features at timestamp t use ONLY events where event_time < t.
    """
    def __init__(self):
        self.customer_history: Dict[str, List[Dict[str, Any]]] = {}

    def extract_features_at_time(
        self,
        customer_id: str,
        amount: float,
        tx_type_str: str,
        current_time: datetime,
        device_id: str,
        merchant_id: str,
        location: str,
        customer_benchmark_avg: float
    ) -> Dict[str, float]:
        history = self.customer_history.get(customer_id, [])

        one_hour_ago = current_time - timedelta(hours=1)
        twenty_four_hours_ago = current_time - timedelta(hours=24)
        thirty_days_ago = current_time - timedelta(days=30)

        # Filter strictly prior: history_timestamp < current_time
        past_1h = [tx for tx in history if tx['timestamp'] < current_time and tx['timestamp'] >= one_hour_ago]
        past_24h = [tx for tx in history if tx['timestamp'] < current_time and tx['timestamp'] >= twenty_four_hours_ago]
        past_30d = [tx for tx in history if tx['timestamp'] < current_time and tx['timestamp'] >= thirty_days_ago]

        velocity_1h = len(past_1h)
        velocity_24h = len(past_24h)

        if past_30d:
            avg_30d = float(np.mean([tx['amount'] for tx in past_30d]))
        elif history:
            all_prior = [tx['amount'] for tx in history if tx['timestamp'] < current_time]
            avg_30d = float(np.mean(all_prior)) if all_prior else customer_benchmark_avg
        else:
            avg_30d = customer_benchmark_avg

        amount_dev_ratio = amount / (avg_30d + 1.0)

        # Most recent prior transaction
        prior_txs = [tx for tx in history if tx['timestamp'] < current_time]
        if prior_txs:
            last_tx = prior_txs[-1]
            time_diff = max(1.0, (current_time - last_tx['timestamp']).total_seconds())
            location_changed = 1.0 if (last_tx['location'] != location) else 0.0
        else:
            time_diff = 86400.0  # 24h baseline
            location_changed = 0.0

        # Novelty checks against prior history
        seen_devices = {tx['device_id'] for tx in prior_txs}
        seen_merchants = {tx['merchant_id'] for tx in prior_txs}

        is_new_device = 0.0 if device_id in seen_devices else 1.0
        is_new_merchant = 0.0 if merchant_id in seen_merchants else 1.0

        tx_type_encoded = float(TX_TYPE_MAP.get(tx_type_str, 1))

        return {
            "amount": float(amount),
            "transaction_type_encoded": tx_type_encoded,
            "hour_of_day": float(current_time.hour),
            "day_of_week": float(current_time.weekday()),
            "transaction_velocity_1h": float(velocity_1h),
            "transaction_velocity_24h": float(velocity_24h),
            "avg_amount_customer_30d": float(avg_30d),
            "amount_deviation_ratio": float(amount_dev_ratio),
            "time_since_last_transaction_seconds": float(time_diff),
            "is_new_device": float(is_new_device),
            "is_new_merchant": float(is_new_merchant),
            "location_changed": float(location_changed)
        }

    def record_transaction(
        self,
        customer_id: str,
        amount: float,
        current_time: datetime,
        device_id: str,
        merchant_id: str,
        location: str
    ):
        if customer_id not in self.customer_history:
            self.customer_history[customer_id] = []
        self.customer_history[customer_id].append({
            "timestamp": current_time,
            "amount": amount,
            "device_id": device_id,
            "merchant_id": merchant_id,
            "location": location
        })


def generate_causal_synthetic_dataset(
    n_customers: int = 600,
    n_merchants: int = 150,
    days: int = 45,
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)

    start_date = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # 1. Generate Entities
    cities = [
        "New York, US", "Los Angeles, US", "Chicago, US", "Houston, US",
        "Phoenix, US", "Philadelphia, US", "San Antonio, US", "San Diego, US",
        "Dallas, US", "San Jose, US", "London, UK", "Paris, FR", "Tokyo, JP",
        "Toronto, CA", "Sydney, AU", "Singapore, SG", "Frankfurt, DE"
    ]
    domestic_cities = cities[:10]
    foreign_cities = cities[10:]

    customers = []
    for i in range(n_customers):
        c_id = f"cust_{i+1:04d}"
        home_city = np.random.choice(domestic_cities)
        base_avg = float(np.random.exponential(scale=65.0) + 20.0)
        primary_dev = f"dev_c_{i+1:04d}_01"
        is_vip = np.random.rand() < 0.06
        if is_vip:
            base_avg = float(np.random.uniform(500.0, 2500.0))
        customers.append({
            "customer_id": c_id,
            "home_city": home_city,
            "base_avg": base_avg,
            "primary_device": primary_dev,
            "is_vip": is_vip,
            "tx_rate_daily": float(np.random.uniform(0.3, 0.9))
        })

    merchants = [f"merch_{j+1:04d}" for j in range(n_merchants)]

    # 2. Plan chronological legitimate events
    events = []
    hn_counts = {
        "STANDARD": 0,
        "TRAVELER_VIP": 0,
        "HOLIDAY_BURST": 0,
        "NEW_MERCHANT": 0,
        "PHONE_UPGRADE": 0
    }

    for cust in customers:
        c_id = cust["customer_id"]
        n_txs = max(2, np.random.poisson(lam=cust["tx_rate_daily"] * days))
        random_seconds = np.sort(np.random.uniform(0, days * 86400, size=n_txs))
        
        for sec in random_seconds:
            tx_time = start_date + timedelta(seconds=float(sec))
            
            hn_type = np.random.choice([
                "STANDARD",
                "TRAVELER_VIP",
                "HOLIDAY_BURST",
                "NEW_MERCHANT",
                "PHONE_UPGRADE"
            ], p=[0.74, 0.07, 0.06, 0.07, 0.06])
            hn_counts[hn_type] += 1

            if hn_type == "TRAVELER_VIP" or cust["is_vip"]:
                amt = float(np.random.uniform(750.0, 7500.0))
                loc = np.random.choice(foreign_cities) if np.random.rand() < 0.65 else cust["home_city"]
                dev = f"dev_travel_{np.random.randint(100, 999)}" if np.random.rand() < 0.4 else cust["primary_device"]
                tx_type = np.random.choice(["CARD_NOT_PRESENT", "WIRE_TRANSFER", "ONLINE_PAYMENT"], p=[0.4, 0.4, 0.2])
            elif hn_type == "HOLIDAY_BURST":
                amt = float(np.random.exponential(scale=cust["base_avg"] * 1.5) + 15.0)
                loc = cust["home_city"]
                dev = cust["primary_device"]
                tx_type = "ONLINE_PAYMENT"
                if np.random.rand() < 0.3:
                    hn_counts["HOLIDAY_BURST"] += 1
                    events.append({
                        "timestamp": tx_time + timedelta(minutes=int(np.random.randint(5, 45))),
                        "customer_id": c_id,
                        "amount": round(float(np.random.exponential(scale=cust["base_avg"]) + 10.0), 2),
                        "transaction_type": "ONLINE_PAYMENT",
                        "device_id": dev,
                        "merchant_id": np.random.choice(merchants),
                        "location": loc,
                        "customer_benchmark_avg": cust["base_avg"],
                        "is_fraud": 0,
                        "fraud_topology": "LEGITIMATE_BURST",
                        "hard_negative_type": "HOLIDAY_BURST"
                    })
            elif hn_type == "NEW_MERCHANT":
                amt = float(np.random.exponential(scale=cust["base_avg"]) + 10.0)
                loc = cust["home_city"]
                dev = cust["primary_device"]
                tx_type = "CARD_NOT_PRESENT"
            elif hn_type == "PHONE_UPGRADE":
                amt = float(np.random.exponential(scale=cust["base_avg"]) + 25.0)
                loc = cust["home_city"]
                dev = f"dev_upgrade_{c_id}"
                tx_type = "CARD_PRESENT"
            else:
                amt = float(np.random.exponential(scale=cust["base_avg"]) + 5.0)
                loc = cust["home_city"]
                dev = cust["primary_device"]
                tx_type = np.random.choice(["CARD_PRESENT", "CARD_NOT_PRESENT", "ONLINE_PAYMENT"], p=[0.6, 0.3, 0.1])

            amt = round(max(5.0, min(15000.0, amt)), 2)
            merch = np.random.choice(merchants)

            events.append({
                "timestamp": tx_time,
                "customer_id": c_id,
                "amount": amt,
                "transaction_type": tx_type,
                "device_id": dev,
                "merchant_id": merch,
                "location": loc,
                "customer_benchmark_avg": cust["base_avg"],
                "is_fraud": 0,
                "fraud_topology": "LEGITIMATE",
                "hard_negative_type": hn_type
            })

    # 3. Inject Realistic Fraud Topologies (~5.2% target prevalence)
    n_normal_events = len(events)
    n_fraud_target = int(n_normal_events * 0.052)

    fraud_targets = np.random.choice(customers, size=min(len(customers), int(n_fraud_target * 0.7)), replace=False)

    topologies = [
        ("ACCOUNT_TAKEOVER", 0.25),
        ("CARD_TESTING", 0.20),
        ("BOT_VELOCITY_ATTACK", 0.20),
        ("OFF_HOURS_WIRE", 0.15),
        ("MERCHANT_ABUSE", 0.10),
        ("DEVICE_TAKEOVER_STEALTH", 0.10)
    ]
    topo_names = [t[0] for t in topologies]
    topo_probs = [t[1] for t in topologies]

    fraud_events = []
    while len(fraud_events) < n_fraud_target:
        target = np.random.choice(fraud_targets)
        c_id = target["customer_id"]
        topo = np.random.choice(topo_names, p=topo_probs)

        f_sec = np.random.uniform(days * 86400 * 0.25, days * 86400)
        f_time = start_date + timedelta(seconds=float(f_sec))

        if topo == "ACCOUNT_TAKEOVER":
            amt = round(float(np.random.uniform(3500.0, 18500.0)), 2)
            dev = f"dev_attacker_{np.random.randint(1000, 9999)}"
            merch = np.random.choice(merchants)
            loc = np.random.choice(foreign_cities)
            tx_type = np.random.choice(["WIRE_TRANSFER", "ONLINE_PAYMENT"], p=[0.75, 0.25])
            fraud_events.append({
                "timestamp": f_time,
                "customer_id": c_id,
                "amount": amt,
                "transaction_type": tx_type,
                "device_id": dev,
                "merchant_id": merch,
                "location": loc,
                "customer_benchmark_avg": target["base_avg"],
                "is_fraud": 1,
                "fraud_topology": topo,
                "hard_negative_type": "NONE"
            })

        elif topo == "CARD_TESTING":
            burst_size = np.random.randint(2, 5)
            dev = f"dev_bot_{np.random.randint(100, 500)}"
            loc = np.random.choice(domestic_cities)
            for b in range(burst_size):
                b_time = f_time + timedelta(seconds=float(b * np.random.uniform(15, 90)))
                amt = round(float(np.random.uniform(12.0, 75.0)), 2)
                fraud_events.append({
                    "timestamp": b_time,
                    "customer_id": c_id,
                    "amount": amt,
                    "transaction_type": "CARD_NOT_PRESENT",
                    "device_id": dev,
                    "merchant_id": np.random.choice(merchants),
                    "location": loc,
                    "customer_benchmark_avg": target["base_avg"],
                    "is_fraud": 1,
                    "fraud_topology": topo,
                    "hard_negative_type": "NONE"
                })

        elif topo == "BOT_VELOCITY_ATTACK":
            burst_size = np.random.randint(3, 6)
            dev = f"dev_botnet_{np.random.randint(500, 999)}"
            loc = target["home_city"] if np.random.rand() < 0.5 else np.random.choice(domestic_cities)
            for b in range(burst_size):
                b_time = f_time + timedelta(seconds=float(b * np.random.uniform(30, 180)))
                amt = round(float(np.random.uniform(80.0, 550.0)), 2)
                fraud_events.append({
                    "timestamp": b_time,
                    "customer_id": c_id,
                    "amount": amt,
                    "transaction_type": "ONLINE_PAYMENT",
                    "device_id": dev,
                    "merchant_id": np.random.choice(merchants),
                    "location": loc,
                    "customer_benchmark_avg": target["base_avg"],
                    "is_fraud": 1,
                    "fraud_topology": topo,
                    "hard_negative_type": "NONE"
                })

        elif topo == "OFF_HOURS_WIRE":
            night_hour = np.random.choice([1, 2, 3, 4])
            f_time = f_time.replace(hour=night_hour, minute=np.random.randint(0, 60))
            amt = round(float(np.random.uniform(4500.0, 16000.0)), 2)
            dev = target["primary_device"] if np.random.rand() < 0.3 else f"dev_night_{np.random.randint(100, 999)}"
            merch = np.random.choice(merchants)
            loc = target["home_city"] if np.random.rand() < 0.4 else np.random.choice(foreign_cities)
            fraud_events.append({
                "timestamp": f_time,
                "customer_id": c_id,
                "amount": amt,
                "transaction_type": "WIRE_TRANSFER",
                "device_id": dev,
                "merchant_id": merch,
                "location": loc,
                "customer_benchmark_avg": target["base_avg"],
                "is_fraud": 1,
                "fraud_topology": topo,
                "hard_negative_type": "NONE"
            })

        elif topo == "MERCHANT_ABUSE":
            amt = round(float(np.random.uniform(600.0, 3800.0)), 2)
            dev = target["primary_device"]
            merch = f"merch_rogue_{np.random.randint(10, 99)}"
            loc = target["home_city"]
            fraud_events.append({
                "timestamp": f_time,
                "customer_id": c_id,
                "amount": amt,
                "transaction_type": "CARD_NOT_PRESENT",
                "device_id": dev,
                "merchant_id": merch,
                "location": loc,
                "customer_benchmark_avg": target["base_avg"],
                "is_fraud": 1,
                "fraud_topology": topo,
                "hard_negative_type": "NONE"
            })

        else: # DEVICE_TAKEOVER_STEALTH
            amt = round(float(np.random.uniform(150.0, 950.0)), 2)
            dev = f"dev_stealth_{np.random.randint(1000, 9999)}"
            merch = np.random.choice(merchants)
            loc = target["home_city"]
            fraud_events.append({
                "timestamp": f_time,
                "customer_id": c_id,
                "amount": amt,
                "transaction_type": "CARD_NOT_PRESENT",
                "device_id": dev,
                "merchant_id": merch,
                "location": loc,
                "customer_benchmark_avg": target["base_avg"],
                "is_fraud": 1,
                "fraud_topology": topo,
                "hard_negative_type": "NONE"
            })

    all_events = events + fraud_events
    # 4. Strictly sort all events chronologically
    all_events.sort(key=lambda x: x["timestamp"])

    # 5. Extract features in strict causal order
    tracker = CausalEntityTracker()
    records = []

    for event in all_events:
        c_id = event["customer_id"]
        t = event["timestamp"]
        amt = event["amount"]
        tx_type = event["transaction_type"]
        dev = event["device_id"]
        merch = event["merchant_id"]
        loc = event["location"]
        bench_avg = event["customer_benchmark_avg"]

        feats = tracker.extract_features_at_time(
            customer_id=c_id,
            amount=amt,
            tx_type_str=tx_type,
            current_time=t,
            device_id=dev,
            merchant_id=merch,
            location=loc,
            customer_benchmark_avg=bench_avg
        )

        record = {
            "timestamp": t.isoformat(),
            "customer_id": c_id,
            "merchant_id": merch,
            "device_id": dev,
            "location": loc,
            "transaction_type": tx_type,
            "is_fraud": event["is_fraud"],
            "fraud_topology": event["fraud_topology"],
            "hard_negative_type": event.get("hard_negative_type", "NONE")
        }
        record.update(feats)
        records.append(record)

        tracker.record_transaction(
            customer_id=c_id,
            amount=amt,
            current_time=t,
            device_id=dev,
            merchant_id=merch,
            location=loc
        )

    df = pd.DataFrame(records)
    return df

def verify_causality_and_leakage(df: pd.DataFrame) -> Dict[str, Any]:
    results = {
        "total_records": len(df),
        "fraud_count": int(df["is_fraud"].sum()),
        "fraud_prevalence_pct": round(float(df["is_fraud"].mean() * 100), 2),
        "is_chronologically_ordered": bool(pd.to_datetime(df["timestamp"]).is_monotonic_increasing),
        "feature_correlations_with_target": {},
        "target_leakage_detected": False,
        "max_correlation": 0.0
    }

    for col in FEATURE_NAMES:
        corr = float(df[col].corr(df["is_fraud"]))
        results["feature_correlations_with_target"][col] = round(corr, 4)
        if abs(corr) > results["max_correlation"]:
            results["max_correlation"] = abs(corr)
        if abs(corr) > 0.95:
            results["target_leakage_detected"] = True

    return results

def generate_and_save_authoritative_dataset(seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = generate_causal_synthetic_dataset(n_customers=600, n_merchants=150, days=45, seed=seed)
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    parquet_path = os.path.join(out_dir, "causal_transactions.parquet")
    df.to_parquet(parquet_path)

    # Compute sha256
    hasher = hashlib.sha256()
    with open(parquet_path, "rb") as f:
        hasher.update(f.read())
    file_sha256 = hasher.hexdigest()

    # Calculate authoritative metadata
    total_tx = len(df)
    n_fraud = int(df["is_fraud"].sum())
    n_legit = total_tx - n_fraud
    fraud_pct = round(float(n_fraud / total_tx * 100), 2)
    
    unique_custs = int(df["customer_id"].nunique())
    unique_merchs = int(df["merchant_id"].nunique())
    unique_devs = int(df["device_id"].nunique())

    topo_counts = df[df["is_fraud"] == 1]["fraud_topology"].value_counts().to_dict()
    topo_pcts = {k: round(float(v / n_fraud * 100), 2) for k, v in topo_counts.items()}

    hn_counts = df[df["is_fraud"] == 0]["hard_negative_type"].value_counts().to_dict()

    timestamps = pd.to_datetime(df["timestamp"])
    start_ts = timestamps.min().isoformat()
    end_ts = timestamps.max().isoformat()

    metadata = {
        "dataset_version": "v2.0.0-forensic",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "sha256_hash": file_sha256,
        "transactions": total_tx,
        "customers": unique_custs,
        "merchants": unique_merchs,
        "devices": unique_devs,
        "days": 45,
        "date_range": {
            "start": start_ts,
            "end": end_ts
        },
        "legitimate_transactions": n_legit,
        "fraudulent_transactions": n_fraud,
        "fraud_rate_pct": fraud_pct,
        "fraud_topologies_counts": topo_counts,
        "fraud_topologies_percentages": topo_pcts,
        "hard_negatives_counts": hn_counts,
        "feature_names": FEATURE_NAMES
    }

    meta_path = os.path.join(out_dir, "forensic_dataset_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Generated authoritative dataset with {total_tx:,} transactions.")
    print(f"Saved to: {parquet_path}")
    print(f"Metadata saved to: {meta_path}")
    return df, metadata

if __name__ == "__main__":
    generate_and_save_authoritative_dataset(seed=42)
