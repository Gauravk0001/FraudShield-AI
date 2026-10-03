export type UserRole = 'ADMIN' | 'FRAUD_ANALYST' | 'RISK_MANAGER' | 'VIEWER';

export interface User {
  id: string;
  organization_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface ShapFactor {
  feature_name: string;
  feature_value: number;
  contribution: number;
  direction: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  explanation: string;
}

export interface RiskExplanation {
  top_factors: ShapFactor[];
  shap_values: Record<string, number>;
}

export interface RiskScore {
  fraud_probability: number;
  anomaly_score: number;
  risk_score: number;
  risk_level: RiskLevel;
  model_version: string;
  behavioral_flags: Record<string, any>;
  explanation?: RiskExplanation;
}

export interface Transaction {
  id: string;
  organization_id: string;
  transaction_id: string;
  customer_id: string;
  merchant_id: string;
  device_id: string;
  amount: number;
  currency: string;
  transaction_type: string;
  location?: string;
  timestamp: string;
  status: 'PENDING' | 'PROCESSED' | 'FAILED' | 'FLAGGED';
  created_at: string;
  risk_score?: RiskScore;
}

export type AlertStatus = 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED' | 'DISMISSED';

export interface Alert {
  id: string;
  organization_id: string;
  transaction_id: string;
  customer_id: string;
  amount: number;
  risk_score: number;
  severity: RiskLevel;
  title: string;
  description: string;
  status: AlertStatus;
  assigned_to_user_id?: string;
  primary_risk_factors: ShapFactor[];
  created_at: string;
  updated_at: string;
}

export type InvestigationStatus = 'OPEN' | 'IN_REVIEW' | 'RESOLVED';
export type InvestigationDecision = 'CONFIRMED_FRAUD' | 'FALSE_POSITIVE' | 'SUSPICIOUS_MONITORED' | 'NO_ACTION_REQUIRED';

export interface InvestigationNote {
  id: string;
  investigation_id: string;
  author_id: string;
  note_text: string;
  created_at: string;
}

export interface Investigation {
  id: string;
  organization_id: string;
  alert_id: string;
  transaction_id: string;
  assigned_analyst_id?: string;
  status: InvestigationStatus;
  decision?: InvestigationDecision;
  decision_reason?: string;
  version: number;
  created_at: string;
  resolved_at?: string;
  notes?: InvestigationNote[];
  alert?: Alert;
  transaction?: Transaction;
}

export interface DashboardStats {
  total_transactions: number;
  high_risk_transactions: number;
  active_alerts: number;
  open_investigations: number;
  fraud_rate_percentage: number;
  avg_latency_ms: number;
}
