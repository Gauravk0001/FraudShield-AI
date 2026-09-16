"""
FraudShield AI — Master Forensic Validation Orchestrator
Runs the complete forensic ML validation pipeline from dataset integrity to final evaluation.
Produces a versioned artifact bundle with full provenance metadata.
"""

import os
import sys
import json
import hashlib
import subprocess
import importlib.metadata
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
ARTIFACTS_BASE = os.path.join(ROOT_DIR, "artifacts")

def banner(msg):
    print(f"\n{'='*64}")
    print(f"  {msg}")
    print(f"{'='*64}")

def step(n, msg):
    print(f"\n[Step {n}] {msg}")

def run_script(script_name: str, args: list = None) -> bool:
    """Run a script file and return True on success."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"  [ERROR] Script not found: {script_path}")
        return False

    cmd = [sys.executable, script_path] + (args or [])
    try:
        result = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=False, timeout=600)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {script_name} exceeded 600 seconds")
        return False

def run_pytest() -> bool:
    """Run full backend test suite."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests", "-v", "--tb=short"],
        cwd=ROOT_DIR,
        capture_output=False,
        timeout=300
    )
    return result.returncode == 0

def get_git_commit_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT_DIR, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"

def get_dataset_hash() -> str:
    parquet_path = os.path.join(ROOT_DIR, "data", "causal_transactions.parquet")
    if os.path.exists(parquet_path):
        with open(parquet_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    return "missing"

def get_model_hash() -> str:
    model_path = os.path.join(ROOT_DIR, "models_artifacts", "fraud_classifier.joblib")
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    return "missing"

def get_next_version(artifacts_base: str) -> str:
    existing = [d for d in Path(artifacts_base).glob("forensic_v*") if d.is_dir()]
    nums = []
    for e in existing:
        try:
            nums.append(int(e.name.replace("forensic_v", "")))
        except Exception:
            pass
    return f"forensic_v{max(nums, default=0) + 1}"

def collect_key_packages() -> dict:
    pkgs = ["xgboost", "scikit-learn", "shap", "pandas", "numpy", "scipy", "joblib", "fastapi"]
    versions = {}
    for pkg in pkgs:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "not-installed"
    return versions

def main():
    banner("FRAUDSHIELD AI — MASTER FORENSIC VALIDATION PIPELINE")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"CWD: {ROOT_DIR}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")

    version_dir = get_next_version(ARTIFACTS_BASE)
    artifact_dir = os.path.join(ARTIFACTS_BASE, version_dir)
    os.makedirs(artifact_dir, exist_ok=True)
    print(f"\nArtifact Directory: {artifact_dir}")

    # Collect run metadata
    run_meta = {
        "run_version": version_dir,
        "git_commit": get_git_commit_hash(),
        "dataset_sha256_prefix": get_dataset_hash(),
        "model_sha256_prefix": get_model_hash(),
        "python_version": sys.version,
        "platform": f"{platform.system()} {platform.release()}",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "random_seeds": [42, 123, 2024, 2025, 777],
        "packages": collect_key_packages(),
        "steps_status": {}
    }

    errors = []

    # ──────────────────────────────────────────────────
    # STEP 1: Dataset Integrity Validation
    # ──────────────────────────────────────────────────
    step(1, "Dataset Integrity Validation")
    ok = run_script("validate_dataset_integrity.py")
    run_meta["steps_status"]["dataset_integrity"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("dataset_integrity")
        print("  [WARN] Dataset integrity check failed — proceeding with caution")

    # ──────────────────────────────────────────────────
    # STEP 2: Final Test Set Manifest Verification
    # ──────────────────────────────────────────────────
    step(2, "Final Test Set Manifest Verification")
    manifest_path = os.path.join(ROOT_DIR, "data", "final_test_manifest.json")
    if os.path.exists(manifest_path):
        ok = run_script("final_test_manifest.py", ["--verify"])
    else:
        print("  [INFO] Generating initial test manifest...")
        ok = run_script("final_test_manifest.py")
    run_meta["steps_status"]["final_test_manifest"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("final_test_manifest")
        print("  [ERROR] Final test set integrity FAILED — stopping pipeline.")
        sys.exit(1)

    # ──────────────────────────────────────────────────
    # STEP 3: Risk Engine Evaluation
    # ──────────────────────────────────────────────────
    step(3, "Composite Risk Engine Evaluation (Weight Grid + Tier Analysis)")
    ok = run_script("evaluate_risk_engine.py")
    run_meta["steps_status"]["risk_engine"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("risk_engine")

    # ──────────────────────────────────────────────────
    # STEP 4: Probability Calibration Evaluation
    # ──────────────────────────────────────────────────
    step(4, "Probability Calibration Evaluation (Uncalibrated/Platt/Isotonic)")
    ok = run_script("evaluate_calibration.py")
    run_meta["steps_status"]["calibration"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("calibration")

    # ──────────────────────────────────────────────────
    # STEP 5: Multi-Seed Stability Evaluation
    # ──────────────────────────────────────────────────
    step(5, "Multi-Seed Stability Evaluation (5 seeds × full retrain)")
    ok = run_script("evaluate_multiseed.py")
    run_meta["steps_status"]["multiseed"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("multiseed")

    # ──────────────────────────────────────────────────
    # STEP 6: Counterfactual Perturbation Analysis
    # ──────────────────────────────────────────────────
    step(6, "Forensic Counterfactual Perturbation Analysis (8 categories)")
    ok = run_script("evaluate_counterfactuals.py")
    run_meta["steps_status"]["counterfactuals"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("counterfactuals")

    # ──────────────────────────────────────────────────
    # STEP 7: Domain Generalization & Shift Evaluation
    # ──────────────────────────────────────────────────
    step(7, "Domain Generalization Evaluation (5 domains + PSI/KS drift)")
    ok = run_script("evaluate_domain_shift.py")
    run_meta["steps_status"]["domain_shift"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("domain_shift")

    # ──────────────────────────────────────────────────
    # STEP 8: Full Automated Test Suite
    # ──────────────────────────────────────────────────
    step(8, "Full Automated Test Suite (pytest backend/tests/)")
    ok = run_pytest()
    run_meta["steps_status"]["pytest"] = "PASS" if ok else "FAIL"
    if not ok:
        errors.append("pytest")

    # ──────────────────────────────────────────────────
    # STEP 9: Finalize Metadata & Copy Key Artifacts
    # ──────────────────────────────────────────────────
    step(9, "Collecting Evaluation Artifacts")
    run_meta["completed_at"] = datetime.now(timezone.utc).isoformat()
    run_meta["overall_status"] = "PASS" if len(errors) == 0 else f"PARTIAL_FAIL (errors: {errors})"
    run_meta["error_steps"] = errors

    # Copy domain results, multiseed results, metadata
    import shutil
    docs_to_copy = [
        "docs/domain_generalization_results.json",
        "docs/multiseed_stability_results.json",
        "data/forensic_dataset_metadata.json",
        "data/final_test_manifest.json"
    ]
    for doc_rel in docs_to_copy:
        src = os.path.join(ROOT_DIR, doc_rel)
        if os.path.exists(src):
            dst = os.path.join(artifact_dir, os.path.basename(src))
            shutil.copy2(src, dst)
            print(f"  Copied: {os.path.basename(src)}")

    run_meta_path = os.path.join(artifact_dir, "run_metadata.json")
    with open(run_meta_path, "w") as f:
        json.dump(run_meta, f, indent=2)
    print(f"  Saved: run_metadata.json")

    # ──────────────────────────────────────────────────
    # Final Summary
    # ──────────────────────────────────────────────────
    banner("FORENSIC VALIDATION PIPELINE COMPLETE")
    print(f"  Version:      {version_dir}")
    print(f"  Git Commit:   {run_meta['git_commit']}")
    print(f"  Dataset Hash: {run_meta['dataset_sha256_prefix']}")
    print(f"  Model Hash:   {run_meta['model_sha256_prefix']}")
    print(f"  Status:       {run_meta['overall_status']}")
    print(f"  Artifacts:    {artifact_dir}")
    print()
    for step_name, status in run_meta["steps_status"].items():
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"    {icon} {step_name:30s} {status}")

    if errors:
        print(f"\n  [WARN] {len(errors)} step(s) had failures: {errors}")
        print("  Review step output above for details.")
        sys.exit(1)
    else:
        print("\n  [SUCCESS] All validation steps passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
