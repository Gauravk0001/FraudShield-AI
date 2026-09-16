import sys
import os
import time
import random
import uuid
from datetime import datetime, timezone

os.environ.setdefault("DB_TYPE", "sqlite")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal, Base, engine
from app.models.user import Organization
from app.services.transaction_service import process_transaction_pipeline
from app.schemas.transaction import TransactionCreate

MERCHANTS_NORMAL = ["Grocery Store #102", "Starbucks Coffee", "Amazon Marketplace", "Target Superstore", "Uber Trip"]
MERCHANTS_SUSPICIOUS = ["Global Crypto Exchange", "Offshore Wire Service", "High Stakes Casino", "Luxury Watch Broker"]
LOCATIONS_NORMAL = ["New York, US", "Chicago, US", "San Francisco, US", "Seattle, US"]
LOCATIONS_SUSPICIOUS = ["Singapore, SG", "Lagos, NG", "Nicosia, CY", "Panama City, PA"]

def run_simulator(count: int = 10, delay_seconds: float = 1.0):
    print(f"=== FraudShield AI Real-Time Transaction Simulator ({count} events) ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    org = db.query(Organization).first()
    org_id = org.id if org else "org_shield_bank"

    for i in range(1, count + 1):
        is_suspicious = (random.random() < 0.3) or (i % 4 == 0) # ~30% suspicious

        if is_suspicious:
            amount = round(random.uniform(2500.0, 15000.0), 2)
            merchant = random.choice(MERCHANTS_SUSPICIOUS)
            location = random.choice(LOCATIONS_SUSPICIOUS)
            device_id = f"dev_unrecognized_{random.randint(100, 999)}"
            tx_type = "wire_transfer"
        else:
            amount = round(random.uniform(5.0, 250.0), 2)
            merchant = random.choice(MERCHANTS_NORMAL)
            location = random.choice(LOCATIONS_NORMAL)
            device_id = "dev_trusted_primary"
            tx_type = "card_present"

        tx_id = f"sim_tx_{uuid.uuid4().hex[:8]}"
        tx_req = TransactionCreate(
            transaction_id=tx_id,
            customer_id=f"cust_{random.randint(101, 105)}",
            merchant_id=merchant,
            device_id=device_id,
            amount=amount,
            currency="USD",
            transaction_type=tx_type,
            location=location,
            timestamp=datetime.now(timezone.utc)
        )

        created_tx, is_dup = process_transaction_pipeline(db, tx_req.model_dump(), org_id)
        risk_score = created_tx.risk_score.risk_score if created_tx.risk_score else 0.0
        risk_level = created_tx.risk_score.risk_level.value if (created_tx.risk_score and hasattr(created_tx.risk_score.risk_level, 'value')) else str(getattr(created_tx.risk_score, 'risk_level', 'LOW'))

        flag_indicator = "[HIGH RISK]" if risk_score >= 70 else ("[MEDIUM]" if risk_score >= 30 else "[LOW]")
        print(f"[{i:02d}/{count:02d}] Tx: {tx_id} | ${amount:8.2f} | {tx_type:14s} | {flag_indicator:11s} (Score: {risk_score:.0f}/100 - {risk_level})")


        time.sleep(delay_seconds)

    db.close()
    print("=== Simulation Complete ===")

if __name__ == "__main__":
    run_simulator(count=5, delay_seconds=0.2)
