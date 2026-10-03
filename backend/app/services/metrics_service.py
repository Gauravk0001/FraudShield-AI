"""
FraudShield AI — Scoring Metrics & Observability Registry

Tracks real-time scoring KPIs, latency percentiles, decision distributions,
model status, and degradation counts in-memory with optional Redis persistence.
"""

import time
import numpy as np
from collections import deque
from typing import Dict, Any, List, Optional
from threading import Lock

class ScoringMetricsRegistry:
    def __init__(self, max_history: int = 5000):
        self._lock = Lock()
        self.total_scored: int = 0
        self.approve_count: int = 0
        self.step_up_count: int = 0
        self.hold_count: int = 0
        self.block_count: int = 0
        self.degraded_count: int = 0
        self.latencies: deque = deque(maxlen=max_history)
        self.active_data_source: str = "paysim_synthetic"
        self.model_version: str = "paysim-v1"
        self.model_load_status: str = "LOADED"
        self.drift_status: str = "NOMINAL"
        self.start_time: float = time.time()

    def record_score(
        self,
        decision: str,
        latency_ms: float,
        degraded: bool = False,
        model_ver: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> None:
        with self._lock:
            self.total_scored += 1
            if decision == "APPROVE":
                self.approve_count += 1
            elif decision == "STEP_UP":
                self.step_up_count += 1
            elif decision == "HOLD_FOR_REVIEW":
                self.hold_count += 1
            elif decision == "BLOCK":
                self.block_count += 1

            if degraded:
                self.degraded_count += 1

            self.latencies.append(float(latency_ms))

            if model_ver:
                self.model_version = model_ver
            if data_source:
                self.active_data_source = data_source

    def set_model_status(self, status: str, version: Optional[str] = None) -> None:
        with self._lock:
            self.model_load_status = status
            if version:
                self.model_version = version

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            lats = list(self.latencies)
            if lats:
                p50 = float(np.percentile(lats, 50))
                p95 = float(np.percentile(lats, 95))
                p99 = float(np.percentile(lats, 99))
                avg_lat = float(np.mean(lats))
            else:
                p50 = 0.0
                p95 = 0.0
                p99 = 0.0
                avg_lat = 0.0

            total = max(1, self.total_scored)
            alert_rate = round(float((self.hold_count + self.step_up_count) / total), 4) if self.total_scored > 0 else 0.0

            return {
                "total_scored": self.total_scored,
                "decisions": {
                    "approve": self.approve_count,
                    "step_up": self.step_up_count,
                    "hold_for_review": self.hold_count,
                    "block": self.block_count
                },
                "alert_rate": alert_rate,
                "degraded_responses": self.degraded_count,
                "latency_ms": {
                    "avg": round(avg_lat, 2),
                    "p50": round(p50, 2),
                    "p95": round(p95, 2),
                    "p99": round(p99, 2)
                },
                "model_status": {
                    "model_load_status": self.model_load_status,
                    "model_version": self.model_version,
                    "active_data_source": self.active_data_source,
                    "drift_status": self.drift_status
                },
                "uptime_seconds": int(time.time() - self.start_time)
            }

metrics_registry = ScoringMetricsRegistry()
