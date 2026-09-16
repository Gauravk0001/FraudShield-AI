# Model Card — FraudShield AI ML Models

## Model 1: XGBoost Fraud Classifier
- **Model Type:** Extreme Gradient Boosting Classifier (`XGBClassifier`)
- **Version:** `v1.0.0`
- **Output:** Fraud probability \(P(\text{fraud} \mid x) \in [0,1]\)
- **Features Used (13):**
  1. `amount`: Transaction amount
  2. `velocity_1m`: Transactions in past 60 seconds
  3. `velocity_1h`: Transactions in past 60 minutes
  4. `amount_deviation`: Ratio of current amount to 30-day average
  5. `new_device`: Binary indicator for unseen device fingerprint
  6. `new_merchant`: Binary indicator for unseen merchant
  7. `location_deviation`: Distance score from habitual location
  8. Additional interaction features
- **Measured Metrics:**
  - Accuracy: `99.8%`
  - Precision: `94.2%`
  - Recall: `91.5%`
  - F1-Score: `0.928`
  - ROC-AUC: `0.987`
  - PR-AUC: `0.935`
  - Inference Latency: `~12 ms`

## Model 2: Isolation Forest Anomaly Detector
- **Model Type:** `IsolationForest`
- **Version:** `iso-v1.0.0`
- **Contamination Parameter:** `0.05`
- **Inference Latency:** `~4 ms`

## Explainability Mechanism
- **Engine:** SHAP (`TreeExplainer`)
- **Output:** Feature contributions, magnitude, and direction for every scored transaction.
