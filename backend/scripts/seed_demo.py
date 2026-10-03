import sys
import os

os.environ.setdefault("DB_TYPE", "sqlite")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.seed_service import seed_demo_environment

if __name__ == "__main__":
    print("============================================================")
    print("FRAUDSHIELD AI — SAFE IDEMPOTENT DEMO SEEDER")
    print("============================================================")
    results = seed_demo_environment(clean_first=False)
    print("Execution Summary:")
    for k, v in results.items():
        print(f"  • {k}: {v}")
    print("============================================================")
