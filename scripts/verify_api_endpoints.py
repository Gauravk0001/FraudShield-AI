import os
import sys
import json

os.environ.setdefault("DB_TYPE", "sqlite")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from app.main import app

def main():
    client = TestClient(app)

    # 1. Health check
    res = client.get('/health')
    print('Health check:', res.status_code, res.json())
    assert res.status_code == 200

    # 2. Login as admin
    login_res = client.post('/api/v1/auth/login', json={'email': 'admin@shieldbank.com', 'password': 'AdminPass123!'})
    assert login_res.status_code == 200, f'Admin login failed: {login_res.text}'
    admin_token = login_res.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    # 3. Login as analyst
    login_analyst = client.post('/api/v1/auth/login', json={'email': 'analyst@shieldbank.com', 'password': 'AnalystPass123!'})
    assert login_analyst.status_code == 200, f'Analyst login failed: {login_analyst.text}'
    analyst_token = login_analyst.json()['access_token']
    analyst_headers = {'Authorization': f'Bearer {analyst_token}'}

    # 4. Dashboard Stats
    stats_res = client.get('/api/v1/dashboard/stats', headers=analyst_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    print('\n--- DASHBOARD STATS ---')
    print(json.dumps(stats, indent=2))
    assert stats['total_transactions'] > 0, 'Total transactions should be > 0'
    assert stats['high_risk_transactions'] > 0, 'High risk count should be > 0'
    assert stats['active_alerts'] > 0, 'Active alerts should be > 0'
    assert stats['open_investigations'] > 0, 'Open investigations should be > 0'

    # 5. Dashboard Trends
    trends_res = client.get('/api/v1/dashboard/trends', headers=analyst_headers)
    assert trends_res.status_code == 200
    trends = trends_res.json()
    print('\n--- DASHBOARD TRENDS (7 Days) ---')
    for t in trends:
        print(f"Date: {t['date']} - Vol: {t['total_volume']} - HighRisk: {t['high_risk']} - AvgRisk: {t['avg_risk_score']}")
    assert len(trends) == 7

    # 6. Transactions List
    tx_res = client.get('/api/v1/transactions?limit=100', headers=analyst_headers)
    assert tx_res.status_code == 200
    txs = tx_res.json()
    print(f'\n--- TRANSACTIONS (Total fetched: {len(txs)}) ---')
    hero_found = any(t['transaction_id'] == 'tx_hero_takeover_007' for t in txs)
    print('Hero transaction tx_hero_takeover_007 present:', hero_found)
    assert hero_found, 'Hero transaction must be present'
    print(f"Sample Tx: {txs[0]['transaction_id']} - ${txs[0]['amount']} - Risk: {txs[0]['risk_score']['risk_score']} ({txs[0]['risk_score']['risk_level']})")

    # 7. Alerts List
    alerts_res = client.get('/api/v1/alerts?limit=100', headers=analyst_headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    print(f'\n--- ALERTS (Total fetched: {len(alerts)}) ---')
    print(f"Sample Alert: {alerts[0]['title']} - Risk: {alerts[0]['risk_score']} - Status: {alerts[0]['status']}")
    assert len(alerts) > 0, 'Alerts should be > 0'

    # 8. Investigations List
    inv_res = client.get('/api/v1/investigations?limit=100', headers=analyst_headers)
    assert inv_res.status_code == 200
    invs = inv_res.json()
    print(f'\n--- INVESTIGATIONS (Total fetched: {len(invs)}) ---')
    for inv in invs:
        print(f"Inv: {inv['id'][:8]} - Status: {inv['status']} - Decision: {inv['decision']} - Notes: {len(inv.get('notes', []))}")
    assert len(invs) >= 3, 'Investigations should be >= 3'

    # 9. Audit Logs
    audit_res = client.get('/api/v1/audit-logs?limit=50', headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    print(f'\n--- AUDIT LOGS (Total fetched: {len(logs)}) ---')
    print(f"Sample Action: {logs[0]['action']} at {logs[0]['created_at']}")

    # 10. Models Registry
    models_res = client.get('/api/v1/models', headers=admin_headers)
    assert models_res.status_code == 200
    print(f'\n--- MODELS REGISTRY ({len(models_res.json())} models) ---')

    # 11. System Settings
    settings_res = client.get('/api/v1/settings', headers=admin_headers)
    assert settings_res.status_code == 200
    print(f"\n--- SETTINGS: Org name = {settings_res.json()['organization_name']}")

    print('\nALL API ENDPOINTS VALIDATED SUCCESSFULLY!')

if __name__ == '__main__':
    main()
