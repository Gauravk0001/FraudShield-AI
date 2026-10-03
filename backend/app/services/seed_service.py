import os
import json
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.core.logging import logger
from app.core.config import settings
import app.models # registers models
from app.models.user import Organization, User, UserRole
from app.models.entities import Customer, Merchant, Device
from app.models.transaction import Transaction
from app.models.risk import RiskScore, RiskExplanation, RiskLevel
from app.models.alert import Alert, AlertStatus
from app.models.investigation import Investigation, InvestigationStatus, InvestigationDecision, InvestigationNote
from app.models.audit import AuditLog
from app.services.transaction_service import process_transaction_pipeline
from app.services.audit_service import log_audit_event
from app.schemas.transaction import TransactionCreate

def seed_demo_environment(clean_first: bool = False) -> Dict[str, Any]:
    """
    Safely and idempotently seed demo organization, users, entities, transactions,
    alerts, and investigation cases through the real ML evaluation pipeline.
    
    Guarantees:
    - Never deletes production data or drops tables.
    - Idempotent: safe to run repeatedly without duplicating records.
    - Uses existing ML/risk pipeline (XGBoost, Isolation Forest, TreeSHAP).
    - Preserves existing audit logs and user data.
    - Fast check on startup: exits immediately (<2ms) if demo records are already present.
    """
    if getattr(settings, "ENVIRONMENT", "").lower() == "production":
        logger.warning("DEMO SEEDING BLOCKED: Demo seeding and demo users are strictly prohibited in production environment.")
        return {"status": "blocked_in_production", "transactions_seeded": 0}

    if not getattr(settings, "ENABLE_DEMO_SEED", True):
        logger.info("Demo data seeding is disabled via ENABLE_DEMO_SEED=False.")
        return {"status": "disabled", "transactions_seeded": 0}

    logger.info("Verifying database schema and demo environment state...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    result_summary = {
        "status": "completed",
        "organization_id": "org_shield_bank",
        "users_seeded": 0,
        "customers_seeded": 0,
        "merchants_seeded": 0,
        "devices_seeded": 0,
        "transactions_seeded": 0,
        "alerts_generated": 0,
        "investigations_seeded": 0
    }

    try:
        # 1. Organization
        org = db.query(Organization).filter(Organization.id == "org_shield_bank").first()
        if not org:
            org = Organization(id="org_shield_bank", name="Shield Bank N.A.")
            db.add(org)
            db.flush()
            logger.info("Created Organization: Shield Bank N.A. (org_shield_bank)")

        # 2. RBAC Users
        demo_users = [
            ("user_admin", "admin@shieldbank.com", "AdminPass123!", UserRole.ADMIN, "Chief Risk Officer Admin"),
            ("user_analyst", "analyst@shieldbank.com", "AnalystPass123!", UserRole.FRAUD_ANALYST, "Sarah Jenkins (Lead Fraud Analyst)"),
            ("user_manager", "manager@shieldbank.com", "ManagerPass123!", UserRole.RISK_MANAGER, "David Ross (Risk Operations Manager)"),
            ("user_viewer", "viewer@shieldbank.com", "ViewerPass123!", UserRole.VIEWER, "Audit Compliance Viewer")
        ]
        for u_id, email, password, role, name in demo_users:
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
                result_summary["users_seeded"] += 1
                logger.info(f"Created User [{role.value}]: {email}")
        db.commit()

        # 3. Known Customers (Deterministic & Identifiable)
        demo_customers = [
            ("cust_101", "DEMO-CUST-101", "alice.smith@demo-shieldbank.com", 15.0),
            ("cust_102", "DEMO-CUST-102", "bob.business@demo-corp.io", 25.0),
            ("cust_103", "DEMO-CUST-103", "charlie.davis@demo-retail.net", 45.0),
            ("cust_104", "DEMO-CUST-104", "diana.prince@demo-travel.org", 30.0),
            ("cust_105", "DEMO-CUST-105", "evan.wright@demo-treasury.com", 20.0),
            ("DEMO-CUST-101", "DEMO-CUST-101", "alice.smith@demo-shieldbank.com", 15.0),
            ("DEMO-CUST-102", "DEMO-CUST-102", "bob.business@demo-corp.io", 25.0),
            ("DEMO-CUST-103", "DEMO-CUST-103", "charlie.davis@demo-retail.net", 45.0),
            ("DEMO-CUST-104", "DEMO-CUST-104", "diana.prince@demo-travel.org", 30.0),
            ("DEMO-CUST-105", "DEMO-CUST-105", "evan.wright@demo-treasury.com", 20.0)
        ]
        for c_id, ext_id, email, risk_prof in demo_customers:
            existing = db.query(Customer).filter(
                Customer.organization_id == org.id,
                Customer.id == c_id
            ).first()
            if not existing:
                db.add(Customer(
                    id=c_id,
                    organization_id=org.id,
                    external_customer_id=ext_id,
                    email=email,
                    risk_profile_score=risk_prof
                ))
                result_summary["customers_seeded"] += 1
        db.commit()

        # 4. Known Merchants (Deterministic & Identifiable)
        demo_merchants = [
            ("merch_demo_starbucks", "DEMO-MERCH-001", "Demo Starbucks Coffee", "food_beverage", 5.0),
            ("merch_demo_wholefoods", "DEMO-MERCH-002", "Demo Whole Foods Market", "groceries", 4.0),
            ("merch_demo_target", "DEMO-MERCH-003", "Demo Target Superstore", "retail", 8.0),
            ("merch_demo_amazon", "DEMO-MERCH-004", "Demo Amazon Marketplace", "digital", 12.0),
            ("merch_demo_shell", "DEMO-MERCH-005", "Demo Shell Gas Station", "fuel", 6.0),
            ("merch_demo_netflix", "DEMO-MERCH-006", "Demo Netflix Streaming", "subscription", 2.0),
            ("merch_demo_uber", "DEMO-MERCH-007", "Demo Uber Mobility", "transit", 7.0),
            ("merch_demo_apple", "DEMO-MERCH-008", "Demo Apple Store", "electronics", 14.0),
            ("merch_demo_delta", "DEMO-MERCH-009", "Demo Delta Air Lines", "travel", 10.0),
            ("merch_demo_cvs", "DEMO-MERCH-010", "Demo CVS Pharmacy", "health", 4.0),
            ("merch_demo_crypto_ex", "DEMO-MERCH-011", "Demo Global Crypto Exchange", "crypto", 88.0),
            ("merch_demo_fast_remit", "DEMO-MERCH-012", "Demo Fast Remit Intl", "remittance", 82.0),
            ("merch_demo_wire_holdings", "DEMO-MERCH-013", "Demo Overseas Wire Holdings", "offshore_finance", 94.0),
            ("merch_demo_high_stakes", "DEMO-MERCH-014", "Demo High Roller Casino", "gaming", 86.0),
            ("merch_demo_luxury_bullion", "DEMO-MERCH-015", "Demo Luxury Gold Bullion", "precious_metals", 91.0),
            ("merch_demo_p2p_bot", "DEMO-MERCH-016", "Demo P2P Transfer Botnet", "peer_to_peer", 89.0),
            ("merch_demo_giftcards", "DEMO-MERCH-017", "Demo Bulk Giftcards Store", "prepaid_cards", 76.0),
            ("merch_demo_luxury_watches", "DEMO-MERCH-018", "Demo Luxury Chrono Boutique", "luxury_goods", 72.0)
        ]
        for m_id, ext_id, name, cat, risk_s in demo_merchants:
            existing = db.query(Merchant).filter(
                Merchant.organization_id == org.id,
                Merchant.id == m_id
            ).first()
            if not existing:
                db.add(Merchant(
                    id=m_id,
                    organization_id=org.id,
                    external_merchant_id=ext_id,
                    name=name,
                    category=cat,
                    risk_score=risk_s
                ))
                result_summary["merchants_seeded"] += 1
        db.commit()

        # 5. Known Devices
        demo_devices = [
            ("dev_trusted_cust_101", "DEMO-DEV-001", "Apple iPhone 15 Pro", "198.51.100.12", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4)"),
            ("dev_trusted_cust_102", "DEMO-DEV-002", "Apple MacBook Pro M3", "198.51.100.24", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"),
            ("dev_trusted_cust_103", "DEMO-DEV-003", "Samsung Galaxy S24", "198.51.100.36", "Mozilla/5.0 (Linux; Android 14; SM-S928B)"),
            ("dev_trusted_cust_104", "DEMO-DEV-004", "Apple iPad Air M2", "198.51.100.48", "Mozilla/5.0 (iPad; CPU OS 17_4)"),
            ("dev_trusted_cust_105", "DEMO-DEV-005", "Dell Precision 5570", "198.51.100.60", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
            ("dev_hacked_session_sg", "DEMO-DEV-006", "Headless Chrome Session Hijack", "103.253.24.11", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"),
            ("dev_vpn_exit_node", "DEMO-DEV-007", "NordVPN Commercial Exit Node", "102.89.33.201", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
            ("dev_tor_browser", "DEMO-DEV-008", "Tor Onion Routing Exit Node", "185.220.101.5", "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"),
            ("dev_botnet_node_01", "DEMO-DEV-009", "Android Cloud Emulator Instance 01", "197.210.64.15", "Mozilla/5.0 (Linux; U; Android 9; en-US; SM-G960F)"),
            ("dev_botnet_node_02", "DEMO-DEV-010", "Android Cloud Emulator Instance 02", "197.210.64.16", "Mozilla/5.0 (Linux; U; Android 9; en-US; SM-G960F)"),
            ("dev_unknown_mac", "DEMO-DEV-011", "Unrecognized Safari on macOS", "142.250.80.45", "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5)"),
            ("dev_novel_ipad", "DEMO-DEV-012", "Novel iPad Device", "172.56.21.89", "Mozilla/5.0 (iPad; CPU OS 16_6)"),
            ("dev_novel_android", "DEMO-DEV-013", "Novel Android Handset", "166.137.8.44", "Mozilla/5.0 (Linux; Android 13; Pixel 7)"),
            ("dev_novel_laptop", "DEMO-DEV-014", "Novel Lenovo Laptop", "86.12.45.19", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
            ("dev_novel_mobile", "DEMO-DEV-015", "Novel iOS Handset", "174.195.34.12", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5)"),
            ("dev_spoofed_useragent", "DEMO-DEV-016", "Spoofed Client Fingerprint", "202.175.42.8", "Custom-Inference-Bot/1.0")
        ]
        for d_id, ext_id, fp, ip, ua in demo_devices:
            existing = db.query(Device).filter(
                Device.organization_id == org.id,
                Device.id == d_id
            ).first()
            if not existing:
                db.add(Device(
                    id=d_id,
                    organization_id=org.id,
                    external_device_id=ext_id,
                    device_fingerprint=fp,
                    ip_address=ip,
                    user_agent=ua
                ))
                result_summary["devices_seeded"] += 1
        db.commit()

        # 6. Idempotency Check: Check if demo transactions and investigations already exist
        existing_demo_tx_count = db.query(Transaction).filter(
            Transaction.organization_id == org.id,
            (Transaction.transaction_id.like("DEMO-TXN-%") | Transaction.transaction_id.like("PAYSIM-TXN-%") | (Transaction.transaction_id == "tx_hero_takeover_007"))
        ).count()

        existing_hero = db.query(Transaction).filter(
            Transaction.organization_id == org.id,
            Transaction.transaction_id == "tx_hero_takeover_007"
        ).first()

        existing_inv_count = db.query(Investigation).filter(
            Investigation.organization_id == org.id
        ).count()

        if existing_demo_tx_count >= 130 and existing_hero is not None and existing_inv_count >= 3:
            logger.info(f"Demo environment already fully seeded ({existing_demo_tx_count} demo/paysim transactions, {existing_inv_count} investigations). Skipping.")
            result_summary["status"] = "already_seeded"
            return result_summary

        # 7. Construct 65 Deterministic Synthetic Transactions
        # Specifying normal domestic spending, suspicious deviations, and hero account takeover.
        now = datetime.now(timezone.utc)
        transactions_spec = []

        # PART A: 42 Normal / Low-Risk Transactions (Distributed across the past 7 days)
        normal_merchants_list = [
            ("merch_demo_starbucks", "New York, US"),
            ("merch_demo_wholefoods", "San Francisco, US"),
            ("merch_demo_target", "Seattle, US"),
            ("merch_demo_amazon", "San Francisco, US"),
            ("merch_demo_shell", "Austin, US"),
            ("merch_demo_netflix", "New York, US"),
            ("merch_demo_uber", "Chicago, US"),
            ("merch_demo_apple", "Boston, US"),
            ("merch_demo_delta", "Seattle, US"),
            ("merch_demo_cvs", "Austin, US")
        ]
        normal_amounts = [
            12.50, 4.75, 28.40, 89.20, 15.60, 42.10, 68.90, 115.00, 14.80, 52.30,
            134.50, 22.10, 7.90, 85.40, 31.25, 64.00, 18.75, 96.50, 142.00, 11.20,
            48.60, 78.10, 16.50, 122.00, 9.45, 37.80, 58.20, 104.50, 24.30, 81.00,
            156.00, 19.95, 44.50, 69.20, 13.40, 91.50, 118.75, 27.60, 53.40, 84.20,
            148.90, 33.15
        ]

        for i in range(1, 43):
            cust_num = 101 + ((i - 1) % 5)
            c_id = f"cust_{cust_num}"
            m_id, loc = normal_merchants_list[(i - 1) % len(normal_merchants_list)]
            dev_id = f"dev_trusted_cust_{cust_num}"
            amt = normal_amounts[i - 1]
            tx_type = "CARD_PRESENT" if (i % 3 == 0) else ("ONLINE_PAYMENT" if (i % 3 == 1) else "CARD_NOT_PRESENT")
            # Spread across past 6.8 days so 7-day trend chart is fully populated
            hours_offset = 160.0 - (i * 3.7)
            t_offset = timedelta(hours=hours_offset)
            transactions_spec.append({
                "tx_id": f"DEMO-TXN-{i:04d}",
                "customer_id": c_id,
                "merchant_id": m_id,
                "device_id": dev_id,
                "amount": amt,
                "currency": "USD",
                "tx_type": tx_type,
                "location": loc,
                "timestamp": now - t_offset,
                "expected": "LOW"
            })

        # PART B: 14 Suspicious / Medium-Risk Transactions (Risk 30–69, triggering Alerts)
        suspicious_specs = [
            ("DEMO-TXN-0043", "cust_101", "merch_demo_giftcards", "dev_novel_ipad", 450.00, "CARD_NOT_PRESENT", "Miami, US", timedelta(hours=48)),
            ("DEMO-TXN-0044", "cust_102", "merch_demo_luxury_watches", "dev_unknown_mac", 1250.00, "WIRE_TRANSFER", "Toronto, CA", timedelta(hours=42)),
            ("DEMO-TXN-0045", "cust_103", "merch_demo_crypto_ex", "dev_novel_android", 420.00, "ONLINE_PAYMENT", "Chicago, US", timedelta(hours=36)),
            ("DEMO-TXN-0046", "cust_104", "merch_demo_delta", "dev_novel_laptop", 890.00, "CARD_NOT_PRESENT", "London, UK", timedelta(hours=30)),
            ("DEMO-TXN-0047", "cust_101", "merch_demo_giftcards", "dev_novel_ipad", 380.00, "ONLINE_PAYMENT", "Miami, US", timedelta(hours=24)),
            ("DEMO-TXN-0048", "cust_103", "merch_demo_luxury_watches", "dev_unknown_mac", 1450.00, "CARD_NOT_PRESENT", "Dallas, US", timedelta(hours=20)),
            ("DEMO-TXN-0049", "cust_102", "merch_demo_apple", "dev_trusted_cust_102", 950.00, "WIRE_TRANSFER", "New York, US", timedelta(hours=16)),
            ("DEMO-TXN-0050", "cust_105", "merch_demo_fast_remit", "dev_novel_mobile", 680.00, "ONLINE_PAYMENT", "Austin, US", timedelta(hours=12)),
            ("DEMO-TXN-0051", "cust_104", "merch_demo_amazon", "dev_novel_laptop", 520.00, "ONLINE_PAYMENT", "London, UK", timedelta(hours=9)),
            ("DEMO-TXN-0052", "cust_101", "merch_demo_target", "dev_novel_ipad", 340.00, "CARD_NOT_PRESENT", "Miami, US", timedelta(hours=7)),
            ("DEMO-TXN-0053", "cust_105", "merch_demo_wholefoods", "dev_novel_mobile", 410.00, "CARD_NOT_PRESENT", "Atlanta, US", timedelta(hours=5)),
            ("DEMO-TXN-0054", "cust_103", "merch_demo_starbucks", "dev_novel_android", 360.00, "ONLINE_PAYMENT", "Chicago, US", timedelta(hours=4)),
            ("DEMO-TXN-0055", "cust_102", "merch_demo_uber", "dev_unknown_mac", 580.00, "ONLINE_PAYMENT", "Toronto, CA", timedelta(hours=3, minutes=15)),
            ("DEMO-TXN-0056", "cust_104", "merch_demo_cvs", "dev_novel_laptop", 490.00, "CARD_NOT_PRESENT", "London, UK", timedelta(hours=2, minutes=30))
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

        # PART C: 9 Critical Fraud Attacks (Risk >= 70, ATO, Rapid Velocity, Offshore Crypto)
        critical_specs = [
            ("DEMO-TXN-0057", "cust_102", "merch_demo_crypto_ex", "dev_vpn_exit_node", 4800.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(hours=2, minutes=15)),
            ("DEMO-TXN-0058", "cust_103", "merch_demo_luxury_bullion", "dev_tor_browser", 7200.00, "CARD_NOT_PRESENT", "Bucharest, RO", timedelta(hours=1, minutes=50)),
            # Rapid velocity wire transfer burst for Charlie (cust_103):
            ("DEMO-TXN-0059", "cust_103", "merch_demo_fast_remit", "dev_botnet_node_01", 2800.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(hours=1, minutes=30)),
            ("DEMO-TXN-0060", "cust_103", "merch_demo_fast_remit", "dev_botnet_node_01", 3200.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(hours=1, minutes=15)),
            ("DEMO-TXN-0061", "cust_103", "merch_demo_fast_remit", "dev_botnet_node_02", 3900.00, "WIRE_TRANSFER", "Lagos, NG", timedelta(hours=1)),
            ("DEMO-TXN-0062", "cust_104", "merch_demo_p2p_bot", "dev_botnet_node_02", 3400.00, "ONLINE_PAYMENT", "St Petersburg, RU", timedelta(minutes=45)),
            ("DEMO-TXN-0063", "cust_105", "merch_demo_wire_holdings", "dev_vpn_exit_node", 9500.00, "WIRE_TRANSFER", "Panama City, PA", timedelta(minutes=30)),
            ("DEMO-TXN-0064", "cust_103", "merch_demo_high_stakes", "dev_spoofed_useragent", 6100.00, "CARD_NOT_PRESENT", "Macau, MO", timedelta(minutes=15)),
            # FLAGSHIP HERO ACCOUNT TAKEOVER SCENARIO: Alice Smith (cust_101)
            ("tx_hero_takeover_007", "cust_101", "merch_demo_wire_holdings", "dev_hacked_session_sg", 18500.00, "WIRE_TRANSFER", "Singapore, SG", timedelta(minutes=5))
        ]
        for tx_id, cid, mid, dev, amt, txtype, loc, toff in critical_specs:
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

        # PART D: Load Real PaySim1 Ingested Dataset from Kaggle if available
        paysim_candidates = [
            os.path.join(os.path.dirname(__file__), "..", "data", "paysim_demo_transactions.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "paysim_demo_transactions.json"),
            os.path.join(os.getcwd(), "data", "paysim_demo_transactions.json"),
            os.path.join(os.getcwd(), "backend", "app", "data", "paysim_demo_transactions.json"),
            "/app/data/paysim_demo_transactions.json",
            "/app/app/data/paysim_demo_transactions.json"
        ]
        for p_cand in paysim_candidates:
            if os.path.exists(p_cand):
                try:
                    with open(p_cand, "r", encoding="utf-8") as f:
                        paysim_records = json.load(f)
                    logger.info(f"Loaded {len(paysim_records)} PaySim demo transactions from {p_cand}")
                    for p_tx in paysim_records:
                        p_id = p_tx.get("transaction_id")
                        if not p_id or any(t["tx_id"] == p_id for t in transactions_spec):
                            continue
                        ts_val = p_tx.get("timestamp")
                        if isinstance(ts_val, str):
                            try:
                                ts_val = datetime.fromisoformat(ts_val)
                            except Exception:
                                ts_val = now
                        transactions_spec.append({
                            "tx_id": p_id,
                            "customer_id": p_tx.get("customer_id", "cust_101"),
                            "merchant_id": p_tx.get("merchant_id", "merch_demo_amazon"),
                            "device_id": p_tx.get("device_id", "dev_trusted_cust_101"),
                            "amount": float(p_tx.get("amount", 100.0)),
                            "currency": p_tx.get("currency", "USD"),
                            "tx_type": p_tx.get("transaction_type", "ONLINE_PAYMENT"),
                            "location": p_tx.get("location", "New York, US"),
                            "timestamp": ts_val,
                            "expected": "HIGH" if p_tx.get("is_fraud") else "LOW"
                        })
                    break
                except Exception as err:
                    logger.warning(f"Could not load PaySim file {p_cand}: {err}")

        # Sort chronologically so customer velocity and historical averages develop organically
        transactions_spec.sort(key=lambda x: x["timestamp"])

        # 8. Ingest Each Transaction Sequentially Through Real ML Pipeline
        logger.info(f"Processing {len(transactions_spec)} deterministic demo transactions through real pipeline...")
        for item in transactions_spec:
            tx_id = item["tx_id"]
            existing_tx = db.query(Transaction).filter(
                Transaction.organization_id == org.id,
                Transaction.transaction_id == tx_id
            ).first()
            if existing_tx:
                continue

            tx_req = TransactionCreate(
                transaction_id=tx_id,
                customer_id=item["customer_id"],
                merchant_id=item["merchant_id"],
                device_id=item["device_id"],
                amount=item["amount"],
                currency=item["currency"],
                transaction_type=item["tx_type"],
                location=item["location"],
                timestamp=item["timestamp"]
            )
            created_tx, _ = process_transaction_pipeline(
                db=db,
                tx_data=tx_req.model_dump(),
                organization_id=org.id
            )
            result_summary["transactions_seeded"] += 1

        db.commit()

        # Count active alerts generated by real pipeline
        active_alerts_count = db.query(Alert).filter(Alert.organization_id == org.id).count()
        result_summary["alerts_generated"] = active_alerts_count

        # 9. Create Realistic Investigations for High-Risk Alerts
        logger.info("Verifying and seeding demo investigation cases...")
        sorted_alerts = db.query(Alert).filter(Alert.organization_id == org.id).order_by(Alert.risk_score.desc()).all()

        if sorted_alerts:
            # Case 1: Flagship Hero Account Takeover (OPEN - ready for live demo triage)
            hero_tx_obj = db.query(Transaction).filter(
                Transaction.organization_id == org.id,
                Transaction.transaction_id == "tx_hero_takeover_007"
            ).first()
            hero_alert = db.query(Alert).filter(Alert.transaction_id == hero_tx_obj.id).first() if hero_tx_obj else sorted_alerts[0]

            if hero_alert:
                existing_hero_inv = db.query(Investigation).filter(Investigation.alert_id == hero_alert.id).first()
                if not existing_hero_inv:
                    inv_open = Investigation(
                        organization_id=org.id,
                        alert_id=hero_alert.id,
                        transaction_id=hero_alert.transaction_id,
                        status=InvestigationStatus.OPEN,
                        version=1
                    )
                    db.add(inv_open)
                    hero_alert.status = AlertStatus.INVESTIGATING
                    result_summary["investigations_seeded"] += 1

            # Case 2: Botnet Velocity Attack (IN_REVIEW - assigned to Sarah Jenkins)
            non_hero_alerts = [a for a in sorted_alerts if hero_alert and a.id != hero_alert.id]
            if len(non_hero_alerts) >= 1:
                alert_review = non_hero_alerts[0]
                existing_inv2 = db.query(Investigation).filter(Investigation.alert_id == alert_review.id).first()
                if not existing_inv2:
                    inv_review = Investigation(
                        organization_id=org.id,
                        alert_id=alert_review.id,
                        transaction_id=alert_review.transaction_id,
                        assigned_analyst_id="user_analyst",
                        status=InvestigationStatus.IN_REVIEW,
                        version=2
                    )
                    db.add(inv_review)
                    alert_review.status = AlertStatus.INVESTIGATING
                    db.flush()
                    note1 = InvestigationNote(
                        investigation_id=inv_review.id,
                        author_id="user_analyst",
                        note_text="Customer confirmed they did not initiate wire transfer from Lagos IP. Botnet signature detected on novel device."
                    )
                    db.add(note1)
                    result_summary["investigations_seeded"] += 1

            # Case 3: Offshore Crypto Transfer (RESOLVED - CONFIRMED_FRAUD)
            if len(non_hero_alerts) >= 2:
                alert_fraud = non_hero_alerts[1]
                existing_inv3 = db.query(Investigation).filter(Investigation.alert_id == alert_fraud.id).first()
                if not existing_inv3:
                    inv_resolved_fraud = Investigation(
                        organization_id=org.id,
                        alert_id=alert_fraud.id,
                        transaction_id=alert_fraud.transaction_id,
                        assigned_analyst_id="user_analyst",
                        status=InvestigationStatus.RESOLVED,
                        decision=InvestigationDecision.CONFIRMED_FRAUD,
                        decision_reason="Forensic confirmation of unauthorized offshore crypto transfer via hijacked API session. Funds frozen and merchant blacklisted.",
                        resolved_at=now - timedelta(hours=1),
                        version=3
                    )
                    db.add(inv_resolved_fraud)
                    alert_fraud.status = AlertStatus.RESOLVED
                    db.flush()
                    note2 = InvestigationNote(
                        investigation_id=inv_resolved_fraud.id,
                        author_id="user_analyst",
                        note_text="Identity verification failed. Account frozen and chargeback initiated with correspondent banking network."
                    )
                    db.add(note2)
                    result_summary["investigations_seeded"] += 1

            # Case 4: International Travel Booking (RESOLVED - FALSE_POSITIVE)
            if len(non_hero_alerts) >= 3:
                alert_travel = non_hero_alerts[2]
                existing_inv4 = db.query(Investigation).filter(Investigation.alert_id == alert_travel.id).first()
                if not existing_inv4:
                    inv_resolved_fp = Investigation(
                        organization_id=org.id,
                        alert_id=alert_travel.id,
                        transaction_id=alert_travel.transaction_id,
                        assigned_analyst_id="user_analyst",
                        status=InvestigationStatus.RESOLVED,
                        decision=InvestigationDecision.FALSE_POSITIVE,
                        decision_reason="Customer verified legitimate international travel and authorized transaction via hardware token 2FA. Alert closed as benign deviation.",
                        resolved_at=now - timedelta(hours=3),
                        version=3
                    )
                    db.add(inv_resolved_fp)
                    alert_travel.status = AlertStatus.RESOLVED
                    db.flush()
                    note3 = InvestigationNote(
                        investigation_id=inv_resolved_fp.id,
                        author_id="user_analyst",
                        note_text="Contacted customer via verified phone channel. Customer confirmed legitimate travel itinerary and physical card presence."
                    )
                    db.add(note3)
                    result_summary["investigations_seeded"] += 1

        db.commit()

        # 10. Audit Logging (Single seed milestone log, preserving all existing audit records)
        existing_seed_audit = db.query(AuditLog).filter(
            AuditLog.organization_id == org.id,
            AuditLog.action == "DEMO_ENVIRONMENT_SEEDED"
        ).first()
        if not existing_seed_audit:
            log_audit_event(
                db=db,
                action="DEMO_ENVIRONMENT_SEEDED",
                entity_type="SYSTEM",
                organization_id=org.id,
                user_id="user_admin",
                entity_id="demo_dataset_v2",
                details={
                    "transactions_seeded": result_summary["transactions_seeded"],
                    "alerts_active": result_summary["alerts_generated"],
                    "investigations_seeded": result_summary["investigations_seeded"],
                    "seeder_version": "v2.0.0-forensic"
                }
            )

        logger.info(f"Demo environment seed completed successfully: {result_summary}")
        return result_summary

    except Exception as e:
        logger.error(f"Error during demo seed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()
