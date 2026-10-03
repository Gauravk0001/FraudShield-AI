"""
FraudShield AI — Real-Time Operational Metrics Endpoint (GET /api/v1/metrics)

Exposes scoring metrics, throughput, latency percentiles (p50/p95/p99),
decision distributions, degraded fallback counts, and active model status.
"""

from fastapi import APIRouter
from typing import Dict, Any
from app.services.metrics_service import metrics_registry

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
def get_operational_metrics():
    """
    Returns real-time scoring metrics, latency percentiles, and model health.
    """
    return metrics_registry.get_metrics_snapshot()
