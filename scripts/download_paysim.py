#!/usr/bin/env python3
"""
FraudShield AI — PaySim Dataset Downloader

Downloads or locates the official PaySim financial fraud simulation dataset:
Target file: PS_20174392719_1491204439457_Log.csv

CRITICAL SAFETY & RESPONSIBLE AI NOTICE:
- PaySim is a SYNTHETIC multi-agent financial simulation, NOT real customer transaction data.
- Never commit raw datasets, credentials, API keys, or customer records to Git.
- 'isFraud' and 'isFlaggedFraud' are ground-truth evaluation labels ONLY.
  They MUST NEVER be used as model inputs or online scoring features.
"""

import os
import sys
import argparse
import glob
import shutil
from pathlib import Path

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
EXPECTED_FILENAME = "PS_20174392719_1491204439457_Log.csv"

def find_existing_paysim(data_dir: str) -> str | None:
    """Check if PaySim CSV already exists in data_dir or its subdirectories."""
    direct_path = os.path.join(data_dir, EXPECTED_FILENAME)
    if os.path.isfile(direct_path):
        return direct_path

    # Search recursively for matching filename
    matches = glob.glob(os.path.join(data_dir, "**", EXPECTED_FILENAME), recursive=True)
    if matches:
        return matches[0]

    # Search for any large CSV that looks like PaySim
    for csv_file in glob.glob(os.path.join(data_dir, "*.csv")):
        try:
            with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
                header = f.readline().strip().split(",")
                if "step" in header and "nameOrig" in header and "nameDest" in header:
                    return csv_file
        except Exception:
            continue

    return None

def has_kaggle_credentials() -> bool:
    """Check if Kaggle API credentials are configured via environment or file."""
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        return True
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    return kaggle_json.is_file()

def print_manual_instructions(data_dir: str):
    """Print step-by-step instructions for manual download."""
    dest_path = os.path.join(data_dir, EXPECTED_FILENAME)
    print("\n" + "=" * 78)
    print("  PAYSIM MANUAL DOWNLOAD INSTRUCTIONS")
    print("=" * 78)
    print("PaySim is hosted on Kaggle and requires user acceptance of dataset terms.")
    print("Please follow these steps to download manually:\n")
    print("  1. Visit the Kaggle PaySim dataset page in your browser:")
    print("     https://www.kaggle.com/datasets/ealaxi/paysim1\n")
    print("  2. Log in and click 'Download' (approx. 470 MB zip / ~1.8 GB uncompressed).\n")
    print(f"  3. Extract '{EXPECTED_FILENAME}' into:")
    print(f"     {dest_path}\n")
    print("  4. Once downloaded, run:")
    print("     python scripts/prepare_paysim.py\n")
    print("=" * 78)
    print("Alternatively, configure Kaggle API credentials:")
    print("  - Place 'kaggle.json' in ~/.kaggle/kaggle.json (or %USERPROFILE%\\.kaggle\\kaggle.json)")
    print("  - OR set KAGGLE_USERNAME and KAGGLE_KEY environment variables.")
    print("Then re-run: python scripts/download_paysim.py")
    print("=" * 78 + "\n")

def download_paysim(data_dir: str = DEFAULT_DATA_DIR, force: bool = False) -> str:
    """Download PaySim dataset via Kaggle CLI / kagglehub if credentials present, or guide user."""
    os.makedirs(data_dir, exist_ok=True)
    target_path = os.path.join(data_dir, EXPECTED_FILENAME)

    if not force:
        existing = find_existing_paysim(data_dir)
        if existing:
            size_mb = os.path.getsize(existing) / (1024 * 1024)
            print(f"[+] PaySim dataset already present at: {existing} ({size_mb:.1f} MB)")
            return existing

    print(f"[*] Checking Kaggle credentials for automated download...")
    if not has_kaggle_credentials():
        print("[-] Kaggle credentials not configured in environment or ~/.kaggle/kaggle.json.")
        print_manual_instructions(data_dir)
        return ""

    try:
        import kagglehub
        print("[*] Kaggle credentials found. Downloading 'ealaxi/paysim1' via kagglehub...")
        download_path = kagglehub.dataset_download("ealaxi/paysim1")
        print(f"[*] Dataset downloaded to staging cache: {download_path}")

        # Locate extracted CSV
        csv_candidates = glob.glob(os.path.join(download_path, "*.csv"))
        if not csv_candidates:
            raise FileNotFoundError(f"No CSV file found in downloaded path: {download_path}")

        src_csv = csv_candidates[0]
        shutil.copy2(src_csv, target_path)
        size_mb = os.path.getsize(target_path) / (1024 * 1024)
        print(f"[+] Successfully copied PaySim dataset to: {target_path} ({size_mb:.1f} MB)")
        return target_path

    except Exception as e:
        print(f"[-] Automated download failed: {e}")
        print_manual_instructions(data_dir)
        return ""

def main():
    parser = argparse.ArgumentParser(description="Download or verify the PaySim dataset for FraudShield AI.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help=f"Destination directory (default: {DEFAULT_DATA_DIR})")
    parser.add_argument("--force", action="store_true", help="Force re-download even if dataset already exists")
    args = parser.parse_args()

    result = download_paysim(data_dir=args.data_dir, force=args.force)
    if result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
