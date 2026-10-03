"""
FraudShield AI — PaySim Feature Engineering & Historical Aggregator

Shared feature-extraction module for PaySim simulation records, supporting both:
1. High-throughput chronological batch feature calculation for training/evaluation splits.
2. Low-latency online feature extraction for real-time /api/v1/score serving.

Guarantees:
- Strictly causal / non-anticipative historical metrics (never uses current or future records).
- Cold-start handling for first-time seen accounts.
- Zero label leakage: 'isFraud' and 'isFlaggedFraud' are never touched.
- Separate extraction paths for with-balance vs. no-balance feature sets.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque

from app.ml.feature_schema import (
    PAYSIM_TYPE_MAP,
    PAYSIM_FEATURES_NO_BALANCE,
    PAYSIM_FEATURES_WITH_BALANCE,
    validate_feature_columns
)

# In-memory online state store for stateful scoring in simulation or test environments
class PaySimOnlineFeatureStore:
    """
    Maintains strictly historical transaction states per entity.
    Updated ONLY AFTER the current transaction has been scored.
    """
    def __init__(self):
        # account_id -> list of (step, amount)
        self.origin_history: Dict[str, List[Tuple[int, float]]] = defaultdict(list)
        # (origin_id, dest_id) -> count of prior transfers
        self.pair_history: Dict[Tuple[str, str], int] = defaultdict(int)
        # dest_id -> count of prior inbound transfers
        self.dest_inbound_history: Dict[str, int] = defaultdict(int)

    def extract_online_features(
        self,
        tx_data: Dict[str, Any],
        with_balance: bool = False
    ) -> Dict[str, float]:
        """
        Extracts features strictly using historical state prior to this transaction.
        Does NOT mutate state here. Call commit_transaction() after scoring.
        """
        step = int(tx_data.get("step", 1))
        tx_type_str = str(tx_data.get("type", tx_data.get("transaction_type", "PAYMENT"))).upper()
        amount = float(tx_data.get("amount", 0.0))
        orig_id = str(tx_data.get("nameOrig", tx_data.get("customer_id", "")))
        dest_id = str(tx_data.get("nameDest", tx_data.get("merchant_id", tx_data.get("destination_account_id", ""))))

        type_encoded = float(PAYSIM_TYPE_MAP.get(tx_type_str, 0))
        log_amount = float(np.log1p(max(0.0, amount)))
        step_hour = float(step % 24)
        step_day = float((step // 24) % 7)

        # Origin historical aggregations strictly prior to this transaction
        prior_txs = self.origin_history.get(orig_id, [])
        # Strictly prior: s < step (or if in same step, strictly prior events in sequence)
        prior_1h = [amt for (s, amt) in prior_txs if s >= step - 1 and s < step]
        prior_6h = [amt for (s, amt) in prior_txs if s >= step - 6 and s < step]
        prior_24h = [amt for (s, amt) in prior_txs if s >= step - 24 and s < step]

        v_1h = float(len(prior_1h))
        v_6h = float(len(prior_6h))
        v_24h = float(len(prior_24h))

        tot_1h = float(sum(prior_1h))
        tot_6h = float(sum(prior_6h))
        tot_24h = float(sum(prior_24h))

        if prior_txs:
            all_prior_amounts = [amt for (_, amt) in prior_txs]
            avg_hist = float(np.mean(all_prior_amounts))
        else:
            # Cold-start baseline: use current amount as proxy baseline (ratio = 1.0)
            avg_hist = float(max(10.0, amount))

        amount_dev_ratio = float(amount / (avg_hist + 1.0))

        # Destination novelty
        prior_pair_count = self.pair_history.get((orig_id, dest_id), 0)
        is_first_time_dest = 1.0 if prior_pair_count == 0 else 0.0
        dest_inbound_count = float(self.dest_inbound_history.get(dest_id, 0))
        is_p2p = 1.0 if dest_id.startswith("C") else 0.0

        features: Dict[str, float] = {
            "amount": float(amount),
            "log_amount": log_amount,
            "type_encoded": type_encoded,
            "step_hour_of_day": step_hour,
            "step_day_of_week": step_day,
            "velocity_origin_1h": v_1h,
            "velocity_origin_6h": v_6h,
            "velocity_origin_24h": v_24h,
            "total_amount_origin_1h": tot_1h,
            "total_amount_origin_6h": tot_6h,
            "total_amount_origin_24h": tot_24h,
            "historical_avg_amount_origin": avg_hist,
            "amount_deviation_ratio": amount_dev_ratio,
            "is_first_time_destination": is_first_time_dest,
            "dest_prior_inbound_count": dest_inbound_count,
            "is_dest_customer_p2p": is_p2p
        }

        if with_balance:
            old_orig = float(tx_data.get("oldbalanceOrg", tx_data.get("oldbalance_org", 0.0)))
            new_orig = float(tx_data.get("newbalanceOrig", tx_data.get("newbalance_orig", 0.0)))
            old_dest = float(tx_data.get("oldbalanceDest", tx_data.get("oldbalance_dest", 0.0)))
            new_dest = float(tx_data.get("newbalanceDest", tx_data.get("newbalance_dest", 0.0)))

            orig_disc = float(new_orig + amount - old_orig)
            dest_disc = float(old_dest + amount - new_dest)
            amt_to_orig = float(amount / (old_orig + 1.0))
            emptied = 1.0 if (old_orig > 0 and new_orig == 0) else 0.0

            features["origin_balance_discrepancy"] = orig_disc
            features["dest_balance_discrepancy"] = dest_disc
            features["amount_to_origin_balance_ratio"] = amt_to_orig
            features["account_emptied_indicator"] = emptied
            features["oldbalance_org"] = old_orig
            features["newbalance_orig"] = new_orig

        return features

    def commit_transaction(self, tx_data: Dict[str, Any]) -> None:
        """Updates internal state strictly AFTER transaction has been scored."""
        step = int(tx_data.get("step", 1))
        amount = float(tx_data.get("amount", 0.0))
        orig_id = str(tx_data.get("nameOrig", tx_data.get("customer_id", "")))
        dest_id = str(tx_data.get("nameDest", tx_data.get("merchant_id", tx_data.get("destination_account_id", ""))))

        self.origin_history[orig_id].append((step, amount))
        self.pair_history[(orig_id, dest_id)] += 1
        self.dest_inbound_history[dest_id] += 1


# Global online store instance
online_feature_store = PaySimOnlineFeatureStore()


def extract_paysim_batch_features(
    df: pd.DataFrame,
    with_balance: bool = False
) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """
    Computes features chronologically across an entire batch DataFrame.
    Guarantees no future leakage: each row computes features strictly
    using prior events.

    Returns:
        (feature_df, labels_series_if_present)
    """
    # Ensure correct chronological order
    df = df.copy()
    if "step" in df.columns:
        df.sort_values(by=["step"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    labels = df["isFraud"].copy() if "isFraud" in df.columns else None

    # Pre-allocate output arrays for speed
    n = len(df)
    v_1h = np.zeros(n, dtype=np.float32)
    v_6h = np.zeros(n, dtype=np.float32)
    v_24h = np.zeros(n, dtype=np.float32)
    tot_1h = np.zeros(n, dtype=np.float32)
    tot_6h = np.zeros(n, dtype=np.float32)
    tot_24h = np.zeros(n, dtype=np.float32)
    hist_avg = np.zeros(n, dtype=np.float32)
    dev_ratio = np.zeros(n, dtype=np.float32)
    first_time_dest = np.zeros(n, dtype=np.float32)
    dest_inbound = np.zeros(n, dtype=np.float32)
    is_p2p = np.zeros(n, dtype=np.float32)

    # State tracking dictionaries
    orig_history: Dict[str, deque] = defaultdict(deque)  # orig -> deque of (step, amount)
    orig_cum_sum: Dict[str, float] = defaultdict(float)
    orig_cum_cnt: Dict[str, int] = defaultdict(int)
    pair_seen = set()
    dest_inbound_cnt: Dict[str, int] = defaultdict(int)

    steps = df["step"].values
    amounts = df["amount"].values
    origs = df["nameOrig"].values
    dests = df["nameDest"].values

    for i in range(n):
        s = steps[i]
        amt = amounts[i]
        orig = origs[i]
        dest = dests[i]

        # 1. Historical aggregations strictly prior to this transaction
        q = orig_history[orig]
        # Evict events older than 24 steps
        while q and q[0][0] < s - 24:
            q.popleft()

        # Count events in prior 1h, 6h, 24h
        c_1 = 0
        c_6 = 0
        c_24 = len(q)
        t_1 = 0.0
        t_6 = 0.0
        t_24 = 0.0

        for past_s, past_amt in q:
            t_24 += past_amt
            if past_s >= s - 6:
                c_6 += 1
                t_6 += past_amt
            if past_s >= s - 1:
                c_1 += 1
                t_1 += past_amt

        v_1h[i] = c_1
        v_6h[i] = c_6
        v_24h[i] = c_24
        tot_1h[i] = t_1
        tot_6h[i] = t_6
        tot_24h[i] = t_24

        # Historical average amount
        prior_cnt = orig_cum_cnt[orig]
        if prior_cnt > 0:
            avg_amt = orig_cum_sum[orig] / prior_cnt
        else:
            avg_amt = max(10.0, amt)
        hist_avg[i] = avg_amt
        dev_ratio[i] = amt / (avg_amt + 1.0)

        # Destination novelty
        pair_key = (orig, dest)
        first_time_dest[i] = 0.0 if pair_key in pair_seen else 1.0
        dest_inbound[i] = dest_inbound_cnt[dest]
        is_p2p[i] = 1.0 if str(dest).startswith("C") else 0.0

        # UPDATE state strictly after computing features
        q.append((s, amt))
        orig_cum_sum[orig] += amt
        orig_cum_cnt[orig] += 1
        pair_seen.add(pair_key)
        dest_inbound_cnt[dest] += 1

    feature_data = {
        "amount": amounts.astype(np.float32),
        "log_amount": np.log1p(np.maximum(0.0, amounts)).astype(np.float32),
        "type_encoded": df["type"].map(lambda t: PAYSIM_TYPE_MAP.get(str(t).upper(), 0)).values.astype(np.float32),
        "step_hour_of_day": (steps % 24).astype(np.float32),
        "step_day_of_week": ((steps // 24) % 7).astype(np.float32),
        "velocity_origin_1h": v_1h,
        "velocity_origin_6h": v_6h,
        "velocity_origin_24h": v_24h,
        "total_amount_origin_1h": tot_1h,
        "total_amount_origin_6h": tot_6h,
        "total_amount_origin_24h": tot_24h,
        "historical_avg_amount_origin": hist_avg,
        "amount_deviation_ratio": dev_ratio,
        "is_first_time_destination": first_time_dest,
        "dest_prior_inbound_count": dest_inbound,
        "is_dest_customer_p2p": is_p2p
    }

    if with_balance:
        old_orig = df["oldbalanceOrg"].values.astype(np.float32)
        new_orig = df["newbalanceOrig"].values.astype(np.float32)
        old_dest = df["oldbalanceDest"].values.astype(np.float32)
        new_dest = df["newbalanceDest"].values.astype(np.float32)

        feature_data["origin_balance_discrepancy"] = new_orig + amounts - old_orig
        feature_data["dest_balance_discrepancy"] = old_dest + amounts - new_dest
        feature_data["amount_to_origin_balance_ratio"] = amounts / (old_orig + 1.0)
        feature_data["account_emptied_indicator"] = ((old_orig > 0) & (new_orig == 0)).astype(np.float32)
        feature_data["oldbalance_org"] = old_orig
        feature_data["newbalance_orig"] = new_orig

    cols = PAYSIM_FEATURES_WITH_BALANCE if with_balance else PAYSIM_FEATURES_NO_BALANCE
    validate_feature_columns(cols)
    out_df = pd.DataFrame(feature_data)[cols]
    return out_df, labels
