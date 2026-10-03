import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  ArrowLeft,
  Lock,
  Eye,
  Database,
  Cpu,
  Layers,
  FileCheck,
  Share2,
  Cookie,
  UserCheck,
  Trash2,
  Baby,
  RefreshCw,
  HelpCircle,
  ExternalLink,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { ThemeToggle } from '../components/shell/ThemeToggle';
import { Footer } from '../components/shell/Footer';
import { Card } from '../components/ui/Card';
import { getStoredToken } from '../services/api';

interface Section {
  id: string;
  title: string;
  icon: React.ElementType;
}

const SECTIONS: Section[] = [
  { id: 'overview', title: '1. Policy Overview', icon: Eye },
  { id: 'info-collected', title: '2. Information We Collect', icon: Database },
  { id: 'how-we-use', title: '3. How We Use Information', icon: Layers },
  { id: 'ml-processing', title: '4. AI & ML Processing', icon: Cpu },
  { id: 'security-measures', title: '5. Security Measures', icon: Lock },
  { id: 'data-retention', title: '6. Data Retention', icon: FileCheck },
  { id: 'data-sharing', title: '7. Data Sharing & Disclosure', icon: Share2 },
  { id: 'third-party', title: '8. Third-Party Services', icon: ExternalLink },
  { id: 'cookies-storage', title: '9. Cookies & Local Storage', icon: Cookie },
  { id: 'user-rights', title: '10. User Rights & Access', icon: UserCheck },
  { id: 'account-deletion', title: '11. Data & Account Deletion', icon: Trash2 },
  { id: 'children-privacy', title: '12. Children\'s Privacy', icon: Baby },
  { id: 'policy-changes', title: '13. Policy Updates', icon: RefreshCw },
  { id: 'contact-privacy', title: '14. Privacy Contact', icon: HelpCircle },
];

export const PrivacyPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('overview');
  const hasAuthToken = !!getStoredToken();
  const backTarget = hasAuthToken ? '/' : '/login';
  const backLabel = hasAuthToken ? 'Back to Console' : 'Back to Sign In';

  const scrollToSection = (id: string) => {
    setActiveSection(id);
    const elem = document.getElementById(id);
    if (elem) {
      elem.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-30 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to={backTarget}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-btn text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{backLabel}</span>
            </Link>

            <div className="h-5 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block" />

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shadow-xs">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-slate-900 dark:text-white text-base tracking-wide leading-tight block">
                  FraudShield AI
                </span>
                <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 font-mono leading-tight block">
                  Data Governance &amp; Privacy Statement
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/terms"
              className="hidden sm:inline-flex items-center text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-1.5 transition-colors"
            >
              Terms &amp; Conditions &rarr;
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Hero Header */}
      <section className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 py-10 px-4 sm:px-6 lg:px-8 transition-colors">
        <div className="max-w-4xl mx-auto text-center sm:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 mb-4">
            <Lock className="w-3.5 h-3.5" />
            <span>Privacy &amp; Data Protection &bull; Version 1.0</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Privacy Policy
          </h1>
          <p className="mt-2 text-sm sm:text-base text-slate-600 dark:text-slate-300">
            How FraudShield AI collects, processes, protects, and governs transaction telemetry and institutional user data.
          </p>
          <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span><strong>Last Updated:</strong> September 28, 2026</span>
            <span>&bull;</span>
            <span><strong>Effective Date:</strong> Immediate</span>
            <span>&bull;</span>
            <span><strong>Data Controller:</strong> Operating Tenant / Enterprise</span>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Sticky Table of Contents (Desktop) */}
          <aside className="hidden lg:block lg:col-span-4 xl:col-span-3">
            <div className="sticky top-24 bg-white dark:bg-slate-900 rounded-card border border-slate-200 dark:border-slate-800 p-4 shadow-xs">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3 px-2">
                Table of Contents
              </h2>
              <nav className="space-y-1 max-h-[calc(100vh-180px)] overflow-y-auto pr-1">
                {SECTIONS.map((sec) => {
                  const Icon = sec.icon;
                  const isActive = activeSection === sec.id;
                  return (
                    <button
                      key={sec.id}
                      onClick={() => scrollToSection(sec.id)}
                      className={`w-full text-left flex items-center justify-between px-2.5 py-2 rounded-btn text-xs transition-colors ${
                        isActive
                          ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 font-semibold'
                          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        <Icon className="w-3.5 h-3.5 shrink-0" />
                        <span className="truncate">{sec.title}</span>
                      </div>
                      <ChevronRight className={`w-3.5 h-3.5 shrink-0 transition-transform ${isActive ? 'rotate-90' : 'opacity-40'}`} />
                    </button>
                  );
                })}
              </nav>

              <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 px-2">
                <Link
                  to="/terms"
                  className="flex items-center justify-between text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  <span>View Terms &amp; Conditions</span>
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </aside>

          {/* Policy Body */}
          <main className="lg:col-span-8 xl:col-span-9 space-y-6">
            {/* Section 1: Overview */}
            <Card id="overview" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Eye className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">1. Policy Overview</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  At <strong>FraudShield AI</strong>, we recognize the mission-critical sensitivity of financial transaction data and organizational identity records. This Privacy Policy details the types of information we process, the specific fraud detection functions for which data is used, the technical safeguards implemented across our application stack, and the controls available to users and subscribing organizations.
                </p>
                <p>
                  FraudShield AI operates primarily as a software provider and risk intelligence platform for institutional tenants. In this capacity, our processing activities are strictly bound by tenant configuration, contractual agreements, and the technical parameters of the deployed platform.
                </p>
              </div>
            </Card>

            {/* Section 2: Information We Collect */}
            <Card id="info-collected" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Database className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">2. Information We Collect</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>To provide real-time fraud scoring and operational workflows, FraudShield AI processes the following categories of data:</p>

                <div className="space-y-3 pt-1">
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-btn border border-slate-200 dark:border-slate-700">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-xs sm:text-sm mb-1">A. User &amp; Account Information</h3>
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      When platform accounts are provisioned, we store the user&rsquo;s full name, corporate email address, securely salted and hashed password representations, assigned Role-Based Access Control (RBAC) role (Fraud Analyst, Risk Manager, Admin, Viewer), and associated Organization ID.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-btn border border-slate-200 dark:border-slate-700">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-xs sm:text-sm mb-1">B. Transaction &amp; Fraud Telemetry Data</h3>
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      Payloads submitted to our ingestion APIs for risk analysis include transaction reference IDs, monetary amounts, currency codes, merchant category codes (MCC), card or account identifiers (tokenized or masked), geolocation telemetry, device risk indicators, velocity indicators, and temporal timestamps.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-btn border border-slate-200 dark:border-slate-700">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-xs sm:text-sm mb-1">C. Technical &amp; Audit Logs</h3>
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      For forensic integrity and platform governance, our backend automatically records immutable audit log events, including user login attempts, threshold modifications, model version updates, manual case dispositions, API request IP addresses, and WebSocket connection states.
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Section 3: How We Use Information */}
            <Card id="how-we-use" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Layers className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">3. How We Use Information</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>We process ingested data strictly for legitimate operational purposes:</p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li><strong>Real-Time Risk Calculation:</strong> Executing ensemble classification algorithms to generate numerical fraud probability scores (0&ndash;100) and severity tiers (LOW, MEDIUM, HIGH, CRITICAL).</li>
                  <li><strong>SHAP Anomaly Attribution:</strong> Generating local feature contribution factors to provide transparent, explainable rationales for flagged transactions.</li>
                  <li><strong>Alert Triage &amp; Case Forensics:</strong> Grouping anomalous activities into triage alerts, populating interactive investigation timelines, and tracking case statuses.</li>
                  <li><strong>System Health &amp; Drift Monitoring:</strong> Calculating portfolio-wide risk distributions, tracking model accuracy metrics, and surfacing concept drift diagnostics.</li>
                  <li><strong>Regulatory Audit Trail:</strong> Maintaining verifiable records of analyst investigations, rationale notes, and supervisory reviews.</li>
                </ul>
              </div>
            </Card>

            {/* Section 4: AI & ML Processing */}
            <Card id="ml-processing" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Cpu className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">4. AI &amp; Machine Learning Processing</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI utilizes supervised and unsupervised machine learning algorithms (such as XGBoost gradient boosting and Isolation Forest outlier detection) alongside configurable heuristic rule matrices.
                </p>
                <p>
                  Where enabled, the AI Copilot provides assistive natural-language synthesis of investigation evidence. All automated AI model outputs are intended as decision-support assistance for human risk specialists (&ldquo;Human-in-the-Loop&rdquo;). FraudShield AI does not enforce automated adverse legal or financial determinations without institutional oversight and configuration.
                </p>
              </div>
            </Card>

            {/* Section 5: Security Measures */}
            <Card id="security-measures" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-emerald-600 dark:text-emerald-400">
                <Lock className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">5. Security Measures &amp; Technical Safeguards</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI implements structured defensive controls to protect data against unauthorized disclosure, interception, or tampering:
                </p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li><strong>Multi-Tenant Data Isolation (RLS):</strong> Organization-level boundary enforcement preventing cross-tenant data leakage.</li>
                  <li><strong>Role-Based Access Control (RBAC):</strong> Strict endpoint permissions dividing analysts, managers, administrators, and view-only accounts.</li>
                  <li><strong>Transit &amp; Authentication Security:</strong> Transport Layer Security (TLS/HTTPS) for all API and WebSocket endpoints, short-lived JWT token authentication, and PBKDF2/bcrypt salted password hashing.</li>
                  <li><strong>Forensic Immutability:</strong> Append-only structured audit logs capturing administrative modifications.</li>
                </ul>
                <div className="p-3 bg-slate-100 dark:bg-slate-800/80 rounded-btn border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400">
                  <div className="flex items-center gap-1.5 font-semibold text-slate-800 dark:text-slate-200 mb-1">
                    <ShieldAlert className="w-4 h-4 text-slate-500" />
                    <span>Realistic Security Disclosure</span>
                  </div>
                  While we apply robust software engineering safeguards and industry best practices, no computer system, cryptographic protocol, or internet transmission can be certified as 100% impenetrable. We commit to continuous security refinement and rapid remediation of verified vulnerabilities.
                </div>
              </div>
            </Card>

            {/* Section 6: Data Retention */}
            <Card id="data-retention" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <FileCheck className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">6. Data Retention Policy</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI retains transaction scoring records, investigation case files, and audit entries for the duration of the subscribing organization&rsquo;s active agreement, subject to institutional compliance and data retention guidelines.
                </p>
                <p>
                  Session tokens and short-lived caching records in memory stores (such as Redis or application cache) expire automatically in accordance with configured timeout policies (e.g. 60-minute default session lifecycles).
                </p>
              </div>
            </Card>

            {/* Section 7: Data Sharing & Disclosure */}
            <Card id="data-sharing" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Share2 className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">7. Data Sharing &amp; Disclosure</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  <strong>FraudShield AI does not sell, rent, monetize, or broker customer transaction data or user personal information.</strong>
                </p>
                <p>Data is shared only in the following strictly controlled scenarios:</p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li><strong>Within Your Subscribing Organization:</strong> Authorized staff members with designated RBAC roles accessing the tenant workspace.</li>
                  <li><strong>Authorized Downstream Integrations:</strong> External systems, webhooks, or third-party core banking services explicitly configured and authorized by your organization.</li>
                  <li><strong>Legal &amp; Regulatory Mandates:</strong> When strictly required by applicable law, court order, or authorized regulatory summons.</li>
                </ul>
              </div>
            </Card>

            {/* Section 8: Third-Party Services */}
            <Card id="third-party" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <ExternalLink className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">8. Third-Party Services</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Depending on tenant configuration, FraudShield AI may interface with third-party service providers (such as cloud hosting providers, managed database services, or external LLM API endpoints for Copilot assistance).
                </p>
                <p>
                  Where external AI copilot capabilities are enabled, only sanitized case metadata necessary for answering the analyst&rsquo;s investigative query is transmitted to the configured API endpoint.
                </p>
              </div>
            </Card>

            {/* Section 9: Cookies & Local Storage */}
            <Card id="cookies-storage" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Cookie className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">9. Cookies &amp; Browser Local Storage</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI does not utilize third-party tracking, profiling, or cross-site advertising cookies. Our frontend application uses browser <code>localStorage</code> strictly for functional platform state:
                </p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li><code>fraudshield_token</code>: Storing the active authenticated session JWT token.</li>
                  <li><code>fraudshield_theme_preference</code>: Storing user preference for Light, Dark, or System visual mode.</li>
                  <li><code>fraudshield_notif_*</code>: Storing local preferences for audio chime alerts, minimum alert severity, and compact table views.</li>
                </ul>
              </div>
            </Card>

            {/* Section 10: User Rights */}
            <Card id="user-rights" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <UserCheck className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">10. User Rights &amp; Access Controls</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Authenticated users may inspect their account profile, review active role assignments, configure notification thresholds, and examine audit activity logs directly within the FraudShield AI Settings and Audit workspaces.
                </p>
                <p>
                  Users seeking modifications to corporate account associations or role permissions should contact their organization&rsquo;s designated FraudShield Platform Administrator.
                </p>
              </div>
            </Card>

            {/* Section 11: Data & Account Deletion */}
            <Card id="account-deletion" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Trash2 className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">11. Data &amp; Account Deletion</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Enterprise administrators may request user deactivation or tenant data de-provisioning upon agreement termination.
                </p>
                <p>
                  Upon confirmed deletion requests, transaction data, model prediction histories, and associated session tokens will be permanently purged in accordance with institutional contract guidelines, barring records required for statutory financial fraud compliance and audit verification.
                </p>
              </div>
            </Card>

            {/* Section 12: Children's Privacy */}
            <Card id="children-privacy" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Baby className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">12. Children&rsquo;s Privacy</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI is an enterprise SaaS cybersecurity and risk operations solution designed exclusively for commercial, institutional, and professional use.
                </p>
                <p>
                  The platform is not directed toward, marketed to, or intended for use by individuals under 18 years of age. We do not knowingly collect personal information from minors.
                </p>
              </div>
            </Card>

            {/* Section 13: Policy Updates */}
            <Card id="policy-changes" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <RefreshCw className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">13. Changes to this Privacy Policy</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  We may periodically update this Privacy Policy to reflect platform evolution, algorithmic enhancements, or changes in regulatory frameworks.
                </p>
                <p>
                  The date of the most recent revision will always be displayed at the top of this page. Your continued use of FraudShield AI following the posting of an updated policy constitutes acknowledgment of the revised practices.
                </p>
              </div>
            </Card>

            {/* Section 14: Contact Privacy */}
            <Card id="contact-privacy" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <HelpCircle className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">14. Privacy &amp; Data Protection Inquiries</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  If you have questions, feedback, or requests regarding this Privacy Policy or our data processing procedures, please contact our data governance desk:
                </p>
                <div className="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-btn border border-slate-200 dark:border-slate-700 space-y-1 font-mono text-xs">
                  <p><span className="text-slate-500 dark:text-slate-400">Privacy Desk:</span> privacy@fraudshield.ai</p>
                  <p><span className="text-slate-500 dark:text-slate-400">Data Protection Officer:</span> dpo@fraudshield.ai</p>
                  <p><span className="text-slate-500 dark:text-slate-400">Security Team:</span> security@fraudshield.ai</p>
                </div>
              </div>
            </Card>
          </main>
        </div>
      </div>

      {/* Reusable Footer */}
      <Footer />
    </div>
  );
};

export default PrivacyPage;
