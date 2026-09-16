import sys
import os
from datetime import datetime, timezone, timedelta

os.environ.setdefault("DB_TYPE", "sqlite")


# Add backend directory to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import Organization, User, UserRole
from app.models.entities import Customer, Merchant, Device
from app.services.transaction_service import process_transaction_pipeline
from app.schemas.transaction import TransactionCreate

def seed_database():
    print("=== Seeding FraudShield AI Demo Database ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Organization
        org = db.query(Organization).filter(Organization.id == "org_shield_bank").first()
        if not org:
            org = Organization(id="org_shield_bank", name="Shield Bank N.A.")
            db.add(org)
            db.flush()
            print("  [+] Organization created: Shield Bank N.A.")

        # 2. Users
        users_data = [
            ("user_admin", "admin@shieldbank.com", "AdminPass123!", UserRole.ADMIN, "Chief Risk Officer Admin"),
            ("user_analyst", "analyst@shieldbank.com", "AnalystPass123!", UserRole.FRAUD_ANALYST, "Sarah Jenkins (Lead Analyst)"),
            ("user_manager", "manager@shieldbank.com", "ManagerPass123!", UserRole.RISK_MANAGER, "David Ross (Risk Manager)"),
            ("user_viewer", "viewer@shieldbank.com", "ViewerPass123!", UserRole.VIEWER, "Audit Compliance Viewer")
        ]

        for u_id, email, password, role, name in users_data:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                u = User(
                    id=u_id,
                    organization_id=org.id,
                    email=email,
                    hashed_password=get_password_hash(password),
                    role=role,
                    full_name=name,
                    is_active=True
                )
                db.add(u)
                print(f"  [+] Seeded User [{role.value}]: {email} (Password: {password})")

        db.commit()

        # 3. Entities (Customer, Merchant, Device)
        customer = db.query(Customer).filter(Customer.id == "cust_101").first()
        if not customer:
            customer = Customer(
                id="cust_101",
                organization_id=org.id,
                external_customer_id="CUST-101",
                email="alice@example.com"
            )
            db.add(customer)

        merchant = db.query(Merchant).filter(Merchant.id == "merch_crypto_exchange").first()
        if not merchant:
            merchant = Merchant(
                id="merch_crypto_exchange",
                organization_id=org.id,
                external_merchant_id="MERCH-CRYPTO",
                name="Global Crypto Exchange",
                category="crypto"
            )
            db.add(merchant)

        device = db.query(Device).filter(Device.id == "dev_unknown_mac").first()
        if not device:
            device = Device(
                id="dev_unknown_mac",
                organization_id=org.id,
                external_device_id="DEV-UNKNOWN",
                device_fingerprint="fp_9988_suspicious"
            )
            db.add(device)


        db.commit()

        # 4. Process Deterministic Normal & Fraud Transactions
        now = datetime.now(timezone.utc)
        print("  [*] Generating deterministic transactions through pipeline...")

        # Normal Tx
        normal_tx = TransactionCreate(
            transaction_id="tx_seed_normal_001",
            customer_id="cust_101",
            merchant_id="merch_grocery",
            device_id="dev_trusted_mac",
            amount=45.50,
            currency="USD",
            transaction_type="purchase",
            location="New York, US",
            timestamp=now - timedelta(minutes=10)
        )
        process_transaction_pipeline(db, normal_tx.model_dump(), org.id)

        # Suspicious High Risk Tx (Triggering Alert & SHAP signals)
        suspicious_tx = TransactionCreate(
            transaction_id="tx_seed_fraud_999",
            customer_id="cust_101",
            merchant_id="merch_crypto_exchange",
            device_id="dev_unknown_mac",
            amount=9850.00,
            currency="USD",
            transaction_type="transfer",
            location="Singapore, SG",
            timestamp=now
        )

        created_tx, _ = process_transaction_pipeline(db, suspicious_tx.model_dump(), org.id)
        print(f"  [!] High-Risk Transaction Processed! ID: {created_tx.id}")


        print("=== Demo Database Seeding Complete Successfully ===")

    except Exception as e:
        print(f"[-] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
