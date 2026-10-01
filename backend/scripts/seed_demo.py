import sys
import os
import random
from datetime import datetime, timezone, timedelta

os.environ.setdefault("DB_TYPE", "sqlite")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import Organization, User, UserRole
from app.models.entities import Customer, Merchant, Device
from app.models.transaction import Transaction
from app.models.risk import RiskScore, RiskExplanation
from app.models.alert import Alert, AlertStatus
from app.models.investigation import Investigation, InvestigationStatus, InvestigationDecision, InvestigationNote
from app.models.audit import AuditLog
from app.services.transaction_service import process_transaction_pipeline
from app.schemas.transaction import TransactionCreate

def seed_demo_environment(clean_first: bool = True):
    print("============================================================")
    print("FRAUDSHIELD AI — COMPETITION DEMO ENGINE SEED")
    print("============================================================")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if clean_first:
            print("  [*] Cleaning previous demo transactions and entities...")
            db.query(InvestigationNote).delete()
            db.query(Investigation).delete()
            db.query(Alert).delete()
            db.query(RiskExplanation).delete()
            db.query(RiskScore).delete()
            db.query(Transaction).delete()
            db.query(AuditLog).delete()
            db.commit()

        # 1. Organization
        org = db.query(Organization).filter(Organization.id == "org_shield_bank").first()
        if not org:
            org = Organization(id="org_shield_bank", name="Shield Bank N.A.")
            db.add(org)
            db.flush()
            print("  [+] Organization: Shield Bank N.A.")

        # 2. Users (RBAC)
        users = [
            ("user_admin", "admin@shieldbank.com", "AdminPass123!", UserRole.ADMIN, "Chief Risk Officer Admin"),
            ("user_analyst", "analyst@shieldbank.com", "AnalystPass123!", UserRole.FRAUD_ANALYST, "Sarah Jenkins (Lead Fraud Analyst)"),
            ("user_manager", "manager@shieldbank.com", "ManagerPass123!", UserRole.RISK_MANAGER, "David Ross (Risk Operations Manager)"),
            ("user_viewer", "viewer@shieldbank.com", "ViewerPass123!", UserRole.VIEWER, "Audit Compliance Viewer")
        ]
        for u_id, email, password, role, name in users:
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
                print(f"  [+] User [{role.value}]: {email}")
        db.commit()

        # 3. Known Customers
        customers = [
            ("cust_101", "CUST-101", "alice@example.com"),
            ("cust_102", "CUST-102", "bob_business@corp.io"),
            ("cust_103", "CUST-103", "charlie@retail.net"),
            ("cust_104", "CUST-104", "diana_traveler@world.org"),
            ("cust_105", "CUST-105", "evan_treasury@finance.com")
        ]
        for c_id, ext_id, email in customers:
            if not db.query(Customer).filter(Customer.id == c_id).first():
                db.add(Customer(id=c_id, organization_id=org.id, external_customer_id=ext_id, email=email))
        db.commit()

        # 4. Generate 40 Deterministic Transactions Through REAL Pipeline
        now = datetime.now(timezone.utc)
        print("  [*] Processing 40 deterministic transactions through real pipeline...")

        transactions_spec = []

        # PART A: 25 NORMAL TRANSACTIONS (LOW Risk: $5 - $220, familiar devices, retail/groceries)
        normal_merchants = [
            ("merch_starbucks", "Starbucks Coffee", "food_beverage"),
            ("merch_wholefoods", "Whole Foods Market", "groceries"),
            ("merch_target", "Target Superstore", "retail"),
            ("merch_amazon", "Amazon Prime", "digital"),
            ("merch_shell", "Shell Gas Station", "fuel"),
            ("merch_netflix", "Netflix Monthly", "subscription"),
            ("merch_uber", "Uber Mobility", "transit")
        ]
        for i in range(1, 26):
            c_id = f"cust_{101 + (i % 5)}"
            m_id, m_name, _ = normal_merchants[i % len(normal_merchants)]
            dev_id = f"dev_trusted_{c_id}"
            amt = round(random.Random(42 + i).uniform(8.50, 185.00), 2)
            t_offset = timedelta(hours=72 - (i * 2.5))
            transactions_spec.append({
                "tx_id": f"tx_norm_{i:03d}",
                "customer_id": c_id,
                "merchant_id": m_id,
                "device_id": dev_id,
                "amount": amt,
                "currency": "USD",
                "tx_type": "CARD_PRESENT" if (i % 3 == 0) else "CARD_NOT_PRESENT",
                "location": "New York, US" if (i % 2 == 0) else "San Francisco, US",
                "timestamp": now - t_offset,
                "expected": "LOW"
            })

        # PART B: 8 SUSPICIOUS TRANSACTIONS (MEDIUM Risk: $350 - $1,450, new devices/merchants, triggering Alerts >= 30)
        suspicious_specs = [
            ("tx_susp_001", "cust_101", "merch_electronics_boutique", "dev_novel_ipad", 540.00, "CARD_NOT_PRESENT", "Miami, US", timedelta(hours=8)),
            ("tx_susp_002", "cust_102", "merch_wholesale_import", "dev_unknown_mac", 1250.00, "WIRE_TRANSFER", "Toronto, CA", timedelta(hours=6)),
            ("tx_susp_003", "cust_103", "merch_crypto_p2p", "dev_novel_android", 420.00, "ONLINE_PAYMENT", "Chicago, US", timedelta(hours=5)),
            ("tx_susp_004", "cust_104", "merch_luxury_hotel", "dev_novel_laptop", 890.00, "CARD_NOT_PRESENT", "London, UK", timedelta(hours=4)),
            ("tx_susp_005", "cust_101", "merch_gaming_credits", "dev_novel_ipad", 380.00, "ONLINE_PAYMENT", "Miami, US", timedelta(hours=3)),
            ("tx_susp_006", "cust_103", "merch_luxury_watches", "dev_unknown_mac", 1450.00, "CARD_NOT_PRESENT", "Dallas, US", timedelta(hours=2)),
            ("tx_susp_007", "cust_102", "merch_hardware_server", "dev_trusted_cust_102", 950.00, "WIRE_TRANSFER", "New York, US", timedelta(hours=1, minutes=45)),
            ("tx_susp_008", "cust_105", "merch_unrecognized_ad", "dev_novel_mobile", 680.00, "ONLINE_PAYMENT", "Austin, US", timedelta(hours=1, minutes=15))
        ]
        for tx_id, cid, mid, dev, amt, txtype, loc, toff in suspicious_specs:
            transactions_spec.append({
                "tx_id": tx_id,
                "customer_id": cid,
                "merchant_id": mid,
                "device_id": dev,
                "amount": amt,
                "currency": "USD",
                "tx_type": txtype,
                "location": loc,
                "timestamp": now - toff,
                "expected": "MEDIUM"
            })

        # PART C: 7 HIGH-RISK HERO FRAUD TRANSACTIONS (HIGH/CRITICAL Risk: $2,800 - $14,500, extreme deviation, foreign location, new device)
        high_risk_specs = [
            # HERO SCENARIO 1: Alice sudden Account Takeover wire transfer to offshore crypto
            ("tx_hero_takeover_001", "cust_101", "merch_crypto_offshore_ltd", "dev_unrecognized_mac_sin", 9850.00, "WIRE_TRANSFER", "Singapore, SG", timedelta(minutes=45)),
            # HERO SCENARIO 2: Charlie rapid bot velocity drainage (3 rapid transfers in 15 mins)
            ("tx_hero_velocity_002", "cust_103", "merch_fast_remit_intl", "dev_botnet_node_01", 2800.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(minutes=25)),
            ("tx_hero_velocity_003", "cust_103", "merch_fast_remit_intl", "dev_botnet_node_01", 3200.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(minutes=20)),
            ("tx_hero_velocity_004", "cust_103", "merch_fast_remit_intl", "dev_botnet_node_02", 3900.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(minutes=15)),
            # HERO SCENARIO 3: Bob treasury account takeover
            ("tx_hero_crypto_005", "cust_102", "merch_crypto_offshore_ltd", "dev_unrecognized_linux", 14500.00, "WIRE_TRANSFER", "Nicosia, CY", timedelta(minutes=10)),
            # HERO SCENARIO 4: Diana compromised credentials
            ("tx_hero_takeover_006", "cust_104", "merch_high_stakes_vip", "dev_unknown_tor_exit", 7800.00, "CARD_NOT_PRESENT", "Panama City, PA", timedelta(minutes=5)),
            # HERO SCENARIO 5: Evan corporate offshore transfer
            ("tx_hero_takeover_007", "cust_105", "merch_crypto_offshore_ltd", "dev_unrecognized_mac_sin", 18500.00, "WIRE_TRANSFER", "Singapore, SG", timedelta(minutes=2))
        ]
        for tx_id, cid, mid, dev, amt, txtype, loc, toff in high_risk_specs:
            transactions_spec.append({
                "tx_id": tx_id,
                "customer_id": cid,
                "merchant_id": mid,
                "device_id": dev,
                "amount": amt,
                "currency": "USD",
                "tx_type": txtype,
                "location": loc,
                "timestamp": now - toff,
                "expected": "HIGH"
            })

        # Process each transaction sequentially through the real pipeline
        low_count = 0
        med_count = 0
        high_count = 0

        for idx, item in enumerate(transactions_spec, 1):
            req = TransactionCreate(
                transaction_id=item["tx_id"],
                customer_id=item["customer_id"],
                merchant_id=item["merchant_id"],
                device_id=item["device_id"],
                amount=item["amount"],
                currency=item["currency"],
                transaction_type=item["tx_type"],
                location=item["location"],
                timestamp=item["timestamp"]
            )
            tx, _ = process_transaction_pipeline(db, req.model_dump(), org.id)
            score = tx.risk_score.risk_score if tx.risk_score else 0.0
            level = tx.risk_score.risk_level.value if tx.risk_score else "LOW"
            
            if score >= 70:
                high_count += 1
            elif score >= 30:
                med_count += 1
            else:
                low_count += 1

            if item["expected"] == "HIGH":
                print(f"  [+] [{idx:02d}/40] HIGH RISK TX: {item['tx_id']} | ${item['amount']:8.2f} | Score: {score:.0f}/100 ({level})")

        print(f"\n  [*] Pipeline Output Summary: Total={len(transactions_spec)} | LOW={low_count} | MEDIUM={med_count} | HIGH={high_count}")

        # 5. Create Realistic Investigations for High-Risk Alerts
        print("  [*] Seeding 3 realistic investigation cases (OPEN, IN_REVIEW, RESOLVED)...")

        # Find alerts created
        alerts = db.query(Alert).filter(Alert.organization_id == org.id).order_by(Alert.risk_score.desc()).all()
        print(f"  [+] Active Alerts generated: {len(alerts)}")

        if len(alerts) >= 3:
            # Case 1: OPEN (Alice's hero account takeover) - for judge demo
            inv_open = Investigation(
                organization_id=org.id,
                alert_id=alerts[0].id,
                transaction_id=alerts[0].transaction_id,
                status=InvestigationStatus.OPEN,
                version=1
            )
            db.add(inv_open)
            db.flush()
            print(f"  [+] Investigation 1 [OPEN]: Alert {alerts[0].id} (Hero Alice Takeover)")

            # Case 2: IN_REVIEW (Charlie bot attack) - assigned to Sarah Jenkins
            inv_review = Investigation(
                organization_id=org.id,
                alert_id=alerts[1].id,
                transaction_id=alerts[1].transaction_id,
                assigned_analyst_id="user_analyst",
                status=InvestigationStatus.IN_REVIEW,
                version=2
            )
            db.add(inv_review)
            db.flush()
            # Add analyst note
            note1 = InvestigationNote(
                investigation_id=inv_review.id,
                author_id="user_analyst",
                note_text="Customer confirmed they did not initiate wire transfer from Lagos IP. Botnet signature detected on device."
            )
            db.add(note1)
            print(f"  [+] Investigation 2 [IN_REVIEW]: Alert {alerts[1].id} (Assigned to Sarah Jenkins)")

            # Case 3: RESOLVED (Bob offshore transfer) - CONFIRMED_FRAUD
            inv_resolved = Investigation(
                organization_id=org.id,
                alert_id=alerts[2].id,
                transaction_id=alerts[2].transaction_id,
                assigned_analyst_id="user_analyst",
                status=InvestigationStatus.RESOLVED,
                decision=InvestigationDecision.CONFIRMED_FRAUD,
                decision_reason="Forensic confirmation of unauthorized offshore crypto transfer via hijacked API session. Funds frozen.",
                resolved_at=now - timedelta(hours=1),
                version=3
            )
            db.add(inv_resolved)
            db.flush()
            note2 = InvestigationNote(
                investigation_id=inv_resolved.id,
                author_id="user_analyst",
                note_text="Identity verification failed. Account frozen and chargeback initiated."
            )
            db.add(note2)
            print(f"  [+] Investigation 3 [RESOLVED]: Alert {alerts[2].id} (Confirmed Fraud)")

        db.commit()
        print("============================================================")
        print("DEMO ENGINE SEED COMPLETE — READY FOR COMPETITION PRESENTATION")
        print("============================================================")

    except Exception as e:
        print(f"[-] Error during seed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_environment(clean_first=True)
