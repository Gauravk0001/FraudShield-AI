"""
FraudShield AI — PaySim1 Dataset Loader & Seeder
Downloads and integrates the official PaySim mobile money fraud dataset from Kaggle via kagglehub.
"""

import os
import sys
import glob
import json
from datetime import datetime, timezone, timedelta
import pandas as pd
import kagglehub

# Setup backend paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.core.database import SessionLocal, Base, engine
from app.models.user import Organization, User, UserRole
from app.models.entities import Customer, Merchant, Device
from app.models.transaction import Transaction
from app.models.alert import Alert, AlertStatus
from app.models.investigation import Investigation, InvestigationStatus, InvestigationDecision, InvestigationNote
from app.services.transaction_service import process_transaction_pipeline
from app.schemas.transaction import TransactionCreate
from app.core.logging import logger

TYPE_MAPPING = {
    "TRANSFER": "WIRE_TRANSFER",
    "PAYMENT": "ONLINE_PAYMENT",
    "CASH_OUT": "CARD_NOT_PRESENT",
    "CASH_IN": "CARD_PRESENT",
    "DEBIT": "CARD_PRESENT"
}

NORMAL_LOCATIONS = [
    "New York, US", "San Francisco, US", "Seattle, US",
    "Chicago, US", "Boston, US", "Austin, US"
]

SUSPICIOUS_LOCATIONS = [
    "Singapore, SG", "Lagos, NG", "Panama City, PA",
    "Bucharest, RO", "Nicosia, CY", "Macau, MO"
]

def load_and_seed_paysim(sample_size: int = 70):
    print("============================================================")
    print("FRAUDSHIELD AI — PAYSIM1 KAGGLEHUB DATASET INGESTION")
    print("============================================================")

    # 1. Download latest version via kagglehub
    print("[*] Downloading latest PaySim1 dataset via kagglehub...")
    path = kagglehub.dataset_download("ealaxi/paysim1")
    print("Path to dataset files:", path)

    csv_files = glob.glob(os.path.join(path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {path}")

    csv_path = csv_files[0]
    print(f"[*] Reading PaySim1 source file: {os.path.basename(csv_path)}")

    # 2. Sample balanced fraud and legitimate rows
    # Read chunk
    df_chunk = pd.read_csv(csv_path, nrows=50000)
    fraud_rows = df_chunk[df_chunk["isFraud"] == 1].copy()
    legit_rows = df_chunk[df_chunk["isFraud"] == 0].copy()

    n_fraud = min(len(fraud_rows), 15)
    n_legit = min(len(legit_rows), sample_size - n_fraud)

    sampled_fraud = fraud_rows.iloc[:n_fraud]
    sampled_legit = legit_rows.iloc[:n_legit]

    print(f"[*] Sampled {len(sampled_legit)} normal records and {len(sampled_fraud)} fraud records from PaySim1.")

    now = datetime.now(timezone.utc)
    demo_records = []

    # Map legitimate rows
    for idx, (_, row) in enumerate(sampled_legit.iterrows(), 1):
        cust_id = f"cust_{101 + (idx % 5)}"
        tx_type = TYPE_MAPPING.get(str(row["type"]).upper(), "ONLINE_PAYMENT")
        loc = NORMAL_LOCATIONS[idx % len(NORMAL_LOCATIONS)]
        dev_id = f"dev_trusted_{cust_id}"
        
        # Temporal spread across the past 7 days
        hours_ago = 160.0 - (idx * (150.0 / n_legit))
        ts = now - timedelta(hours=hours_ago)

        demo_records.append({
            "transaction_id": f"PAYSIM-TXN-{idx:04d}",
            "customer_id": cust_id,
            "merchant_id": str(row["nameDest"]),
            "device_id": dev_id,
            "amount": round(float(row["amount"]), 2),
            "currency": "USD",
            "transaction_type": tx_type,
            "location": loc,
            "timestamp": ts,
            "paysim_type": str(row["type"]),
            "is_fraud": 0
        })

    # Map fraud rows
    for idx, (_, row) in enumerate(sampled_fraud.iterrows(), 1):
        f_idx = n_legit + idx
        cust_id = f"cust_{101 + ((idx + 2) % 5)}"
        tx_type = TYPE_MAPPING.get(str(row["type"]).upper(), "WIRE_TRANSFER")
        loc = SUSPICIOUS_LOCATIONS[idx % len(SUSPICIOUS_LOCATIONS)]
        dev_id = f"dev_novel_{row['nameOrig'][:8].lower()}"

        # Recent timestamps (past 1-12 hours)
        hours_ago = max(0.5, 12.0 - idx)
        ts = now - timedelta(hours=hours_ago)

        demo_records.append({
            "transaction_id": f"PAYSIM-TXN-{f_idx:04d}",
            "customer_id": cust_id,
            "merchant_id": str(row["nameDest"]),
            "device_id": dev_id,
            "amount": round(float(row["amount"]), 2),
            "currency": "USD",
            "transaction_type": tx_type,
            "location": loc,
            "timestamp": ts,
            "paysim_type": str(row["type"]),
            "is_fraud": 1
        })

    # Preserve flagship hero scenario
    hero_tx = {
        "transaction_id": "tx_hero_takeover_007",
        "customer_id": "cust_101",
        "merchant_id": "merch_demo_wire_holdings",
        "device_id": "dev_hacked_session_sg",
        "amount": 18500.00,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER",
        "location": "Singapore, SG",
        "timestamp": now - timedelta(minutes=5),
        "paysim_type": "TRANSFER",
        "is_fraud": 1
    }
    demo_records.append(hero_tx)

    # Sort chronologically
    demo_records.sort(key=lambda x: x["timestamp"])

    # 3. Save to data/
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "paysim_demo_transactions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([
            {**r, "timestamp": r["timestamp"].isoformat()} for r in demo_records
        ], f, indent=2)
    print(f"[+] Saved PaySim demo dataset JSON to: {json_path}")

    # 4. Ingest into database through real ML pipeline
    print(f"[*] Ingesting {len(demo_records)} PaySim transactions into FraudShield database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        org = db.query(Organization).filter(Organization.id == "org_shield_bank").first()
        if not org:
            org = Organization(id="org_shield_bank", name="Shield Bank N.A.")
            db.add(org)
            db.flush()

        seeded_count = 0
        for r in demo_records:
            tx_id = r["transaction_id"]
            existing = db.query(Transaction).filter(
                Transaction.organization_id == org.id,
                Transaction.transaction_id == tx_id
            ).first()
            if existing:
                continue

            tx_req = TransactionCreate(
                transaction_id=tx_id,
                customer_id=r["customer_id"],
                merchant_id=r["merchant_id"],
                device_id=r["device_id"],
                amount=r["amount"],
                currency=r["currency"],
                transaction_type=r["transaction_type"],
                location=r["location"],
                timestamp=r["timestamp"]
            )
            process_transaction_pipeline(db, tx_req.model_dump(), org.id)
            seeded_count += 1

        db.commit()
        print(f"[+] Successfully seeded {seeded_count} PaySim transactions through real ML pipeline.")

        # Update alerts & investigations
        total_tx = db.query(Transaction).filter(Transaction.organization_id == org.id).count()
        total_alerts = db.query(Alert).filter(Alert.organization_id == org.id).count()
        total_invs = db.query(Investigation).filter(Investigation.organization_id == org.id).count()
        print(f"[+] Current Database State: {total_tx} Transactions | {total_alerts} Alerts | {total_invs} Investigations")
        print("============================================================")

    except Exception as e:
        db.rollback()
        print(f"[-] Error seeding PaySim records: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    load_and_seed_paysim()
