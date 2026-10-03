#!/usr/bin/env python3
"""
FraudShield AI — Real-Time HTTP Transaction Simulator

Replays transactions against the live HTTP scoring API (POST /api/v1/score).
Supports:
1. PaySim locked-test-split replay in strict chronological step order.
2. Synthetic streaming generation without dataset files.
3. Configurable streaming rate (transactions/sec) and test duration.
4. Optional fraud oversampling (--fraud-boost).
5. Offline precision/recall evaluation using local ground truth labels.
6. Execution summary output to reports/simulation_runs/.

CRITICAL PRIVACY & LEAKAGE POLICIES:
- Ground-truth labels ('isFraud', 'isFlaggedFraud') are NEVER sent in API request payloads.
- Labels are kept strictly local in the simulator client for offline metric comparison.
- Metrics are clearly marked as synthetic/offline evaluations, not live production monitoring.
"""

import os
import sys
import time
import json
import uuid
import random
import argparse
import numpy as np
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

DEFAULT_API_URL = "http://localhost:8000/api/v1/score"
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DEFAULT_REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports", "simulation_runs"))

def load_paysim_test_data(data_dir: str) -> List[Dict[str, Any]]:
    """Loads PaySim locked-test split records for realistic chronological replay."""
    replay_json = os.path.join(data_dir, "paysim_test_replay.json")
    if os.path.isfile(replay_json):
        with open(replay_json, "r", encoding="utf-8") as f:
            return json.load(f)

    test_parquet = os.path.join(data_dir, "paysim_test.parquet")
    if os.path.isfile(test_parquet):
        import pandas as pd
        df = pd.read_parquet(test_parquet)
        records = []
        for _, row in df.head(1000).iterrows():
            records.append({
                "step": int(row.get("step_hour_of_day", 1)),
                "type": "TRANSFER",
                "amount": float(row.get("amount", 100.0)),
                "nameOrig": f"C{random.randint(1000000, 9999999)}",
                "nameDest": f"M{random.randint(1000000, 9999999)}",
                "oldbalanceOrg": float(row.get("oldbalance_org", 1000.0)),
                "newbalanceOrig": float(row.get("newbalance_orig", 0.0)),
                "isFraud": int(row.get("target_is_fraud", 0))
            })
        return records

    # Synthetic sample fallback
    sample_csv = os.path.join(data_dir, "paysim_synthetic_sample.csv")
    if os.path.isfile(sample_csv):
        import pandas as pd
        df = pd.read_csv(sample_csv)
        return df.tail(1000).to_dict(orient="records")

    return []

def generate_synthetic_record() -> Tuple[Dict[str, Any], int]:
    """Generates a synthetic transaction payload and local ground-truth fraud label."""
    is_fraud = 1 if (random.random() < 0.08) else 0

    if is_fraud:
        amount = round(random.uniform(5000.0, 45000.0), 2)
        tx_type = random.choice(["TRANSFER", "WIRE_TRANSFER", "CASH_OUT"])
        merchant = random.choice(["Global Offshore Wire Ltd", "Panama Crypto Exchange", "QuickCash Terminal #88"])
        location = random.choice(["Singapore, SG", "Lagos, NG", "Panama City, PA", "Nicosia, CY"])
        dev_id = f"dev_novel_{uuid.uuid4().hex[:6]}"
        old_bal = amount
        new_bal = 0.0
    else:
        amount = round(random.uniform(5.0, 350.0), 2)
        tx_type = random.choice(["CARD_PRESENT", "ONLINE_PAYMENT", "PAYMENT"])
        merchant = random.choice(["Target Superstore #104", "Starbucks Coffee", "Amazon Marketplace", "Trader Joe's"])
        location = random.choice(["New York, US", "Chicago, US", "San Francisco, US", "Seattle, US"])
        dev_id = "dev_trusted_primary"
        old_bal = amount * 3.5
        new_bal = old_bal - amount

    tx_id = f"sim_tx_{uuid.uuid4().hex[:8]}"
    payload = {
        "transaction_id": tx_id,
        "customer_id": f"cust_{random.randint(101, 120)}",
        "merchant_id": merchant,
        "device_id": dev_id,
        "amount": amount,
        "currency": "USD",
        "transaction_type": tx_type,
        "location": location,
        "step": random.randint(630, 744),
        "nameOrig": f"C{random.randint(1000000, 9999999)}",
        "nameDest": f"M{random.randint(1000000, 9999999)}",
        "oldbalanceOrg": old_bal,
        "newbalanceOrig": new_bal
    }
    return payload, is_fraud

def run_simulation(
    source: str = "synthetic",
    api_url: str = DEFAULT_API_URL,
    rate: float = 5.0,
    fraud_boost: float = 1.0,
    duration: int = 30,
    api_key: Optional[str] = None,
    seed: int = 42
) -> Dict[str, Any]:
    print("=" * 78)
    print("  FRAUDSHIELD AI — LIVE HTTP TRANSACTION SCORING SIMULATOR")
    print("=" * 78)
    print(f"[*] Target API Endpoint:  {api_url}")
    print(f"[*] Data Source:          {source.upper()}")
    print(f"[*] Stream Rate:          {rate:.1f} tx/sec")
    print(f"[*] Fraud Boost:          {fraud_boost:.1f}x")
    print(f"[*] Duration:             {duration} seconds")
    print("=" * 78)

    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(DEFAULT_REPORTS_DIR, exist_ok=True)

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    # Load records if source is paysim
    paysim_records = []
    if source.lower() == "paysim":
        paysim_records = load_paysim_test_data(DEFAULT_DATA_DIR)
        if not paysim_records:
            print("[-] No PaySim test records found. Falling back to synthetic stream.")
            source = "synthetic"
        else:
            print(f"[+] Loaded {len(paysim_records):,} PaySim test split records for replay.")

    interval = 1.0 / max(0.1, rate)
    start_time = time.time()
    end_time = start_time + duration

    total_sent = 0
    decision_counts = {"APPROVE": 0, "STEP_UP": 0, "HOLD_FOR_REVIEW": 0, "BLOCK": 0}
    latencies = []
    y_true_list = []
    y_pred_hold_list = []
    degraded_count = 0

    idx = 0
    while time.time() < end_time:
        loop_start = time.perf_counter()

        # Select or generate record
        if source.lower() == "paysim" and paysim_records:
            record = paysim_records[idx % len(paysim_records)]
            idx += 1
            local_fraud = int(record.get("isFraud", 0))

            # Apply fraud-boost oversampling if enabled
            if fraud_boost > 1.0 and local_fraud == 0:
                if random.random() < (1.0 - (1.0 / fraud_boost)):
                    # Look ahead for a fraud record to substitute
                    for candidate in paysim_records:
                        if candidate.get("isFraud") == 1:
                            record = candidate
                            local_fraud = 1
                            break

            # Construct clean request payload (EXCLUDE all label columns)
            payload = {
                "transaction_id": f"sim_paysim_{uuid.uuid4().hex[:8]}",
                "amount": float(record.get("amount", 100.0)),
                "currency": "USD",
                "step": int(record.get("step", 1)),
                "type": str(record.get("type", "TRANSFER")),
                "nameOrig": str(record.get("nameOrig", "C_ORIG")),
                "nameDest": str(record.get("nameDest", "M_DEST")),
                "oldbalanceOrg": float(record.get("oldbalanceOrg", 0.0)),
                "newbalanceOrig": float(record.get("newbalanceOrig", 0.0)),
                "oldbalanceDest": float(record.get("oldbalanceDest", 0.0)),
                "newbalanceDest": float(record.get("newbalanceDest", 0.0))
            }
        else:
            payload, local_fraud = generate_synthetic_record()

        # Execute HTTP POST to scoring endpoint
        try:
            req_start = time.perf_counter()
            resp = requests.post(api_url, json=payload, headers=headers, timeout=5.0)
            req_latency = (time.perf_counter() - req_start) * 1000.0

            if resp.status_code == 200:
                data = resp.json()
                decision = data.get("decision", "APPROVE")
                risk_score = data.get("risk_score", 0.0)
                prob = data.get("fraud_probability", 0.0)
                is_degraded = data.get("degraded", False)

                total_sent += 1
                latencies.append(req_latency)
                decision_counts[decision] = decision_counts.get(decision, 0) + 1
                if is_degraded:
                    degraded_count += 1

                y_true_list.append(local_fraud)
                is_hold = 1 if decision in ["HOLD_FOR_REVIEW", "BLOCK"] else 0
                y_pred_hold_list.append(is_hold)

                # Format terminal log
                dec_color = "[HOLD_FOR_REVIEW]" if decision == "HOLD_FOR_REVIEW" else (
                    "[STEP_UP]" if decision == "STEP_UP" else "[APPROVE]"
                )
                fraud_tag = "[FRAUD LABEL]" if local_fraud == 1 else "[LEGIT LABEL]"
                print(
                    f"[{total_sent:04d}] Tx: {payload.get('transaction_id')} | "
                    f"${payload.get('amount'):>9.2f} | {payload.get('type', payload.get('transaction_type')):<12s} | "
                    f"{dec_color:<18s} (Risk: {risk_score:>4.1f}, p={prob:.2f}, {req_latency:>5.1f}ms) | {fraud_tag}"
                )
            else:
                print(f"[-] HTTP Error {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"[-] Connection failed to {api_url}: {e}")
            break

        # Rate throttle
        elapsed = time.perf_counter() - loop_start
        sleep_dur = max(0.0, interval - elapsed)
        time.sleep(sleep_dur)

    # 4. Summary & Evaluation
    print("=" * 78)
    print("  SIMULATION RUN COMPLETED — SUMMARY REPORT")
    print("=" * 78)
    avg_lat = float(np.mean(latencies)) if latencies else 0.0
    p95_lat = float(np.percentile(latencies, 95)) if latencies else 0.0
    p99_lat = float(np.percentile(latencies, 99)) if latencies else 0.0

    holds = decision_counts.get("HOLD_FOR_REVIEW", 0) + decision_counts.get("BLOCK", 0)
    alert_rate = float(holds / max(1, total_sent))

    # Offline Precision & Recall
    tp = sum(1 for yt, yp in zip(y_true_list, y_pred_hold_list) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true_list, y_pred_hold_list) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true_list, y_pred_hold_list) if yt == 1 and yp == 0)
    tn = sum(1 for yt, yp in zip(y_true_list, y_pred_hold_list) if yt == 0 and yp == 0)

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print(f"Total Transactions Sent:  {total_sent}")
    print(f"Decisions Breakdown:      {decision_counts}")
    print(f"Alert / Hold Rate:        {alert_rate*100:.2f}%")
    print(f"Degraded Fallbacks:       {degraded_count}")
    print(f"Average Latency:          {avg_lat:.2f} ms")
    print(f"p95 Latency:              {p95_lat:.2f} ms")
    print(f"p99 Latency:              {p99_lat:.2f} ms")
    print(f"Observed Precision:       {precision:.4f} (at HOLD threshold)")
    print(f"Observed Recall:          {recall:.4f}")
    print(f"Observed F1:              {f1:.4f}")
    print("-" * 78)
    print("NOTICE: Simulator metrics represent offline evaluation against synthetic data, NOT production monitoring.")
    print("=" * 78)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "api_url": api_url,
        "total_sent": total_sent,
        "decisions": decision_counts,
        "alert_rate": round(alert_rate, 4),
        "degraded_count": degraded_count,
        "latency_ms": {
            "avg": round(avg_lat, 2),
            "p95": round(p95_lat, 2),
            "p99": round(p99_lat, 2)
        },
        "offline_metrics": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn
        },
        "disclaimer": "Synthetic offline evaluation metrics only. Not real production customer data."
    }

    report_path = os.path.join(DEFAULT_REPORTS_DIR, f"sim_run_{int(time.time())}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[+] Saved simulation summary report to: {report_path}")

    return summary

def main():
    parser = argparse.ArgumentParser(description="Real-Time HTTP Transaction Simulator for FraudShield AI.")
    parser.add_argument("--source", default="synthetic", choices=["paysim", "synthetic"], help="Data stream source")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Scoring API URL (default: http://localhost:8000/api/v1/score)")
    parser.add_argument("--rate", type=float, default=5.0, help="Transactions per second (default: 5.0)")
    parser.add_argument("--fraud-boost", type=float, default=1.0, help="Oversample fraud rate multiplier (default: 1.0)")
    parser.add_argument("--duration", type=int, default=15, help="Simulation duration in seconds (default: 15)")
    parser.add_argument("--api-key", default=None, help="Optional API key for authorization")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    run_simulation(
        source=args.source,
        api_url=args.api_url,
        rate=args.rate,
        fraud_boost=args.fraud_boost,
        duration=args.duration,
        api_key=args.api_key,
        seed=args.seed
    )

if __name__ == "__main__":
    main()
