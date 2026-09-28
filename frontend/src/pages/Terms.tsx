import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  ArrowLeft,
  FileText,
  AlertTriangle,
  Cpu,
  Lock,
  Scale,
  Database,
  Building,
  RefreshCw,
  HelpCircle,
  ExternalLink,
  ShieldAlert,
  Layers,
  ChevronRight,
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
  { id: 'introduction', title: '1. Introduction', icon: FileText },
  { id: 'acceptance', title: '2. Acceptance of Terms', icon: Scale },
  { id: 'service-description', title: '3. Description of Service', icon: Layers },
  { id: 'user-responsibilities', title: '4. User Responsibilities', icon: ShieldCheck },
  { id: 'account-auth', title: '5. Account & Authentication', icon: Lock },
  { id: 'fraud-disclaimer', title: '6. Fraud & Risk Disclaimer', icon: AlertTriangle },
  { id: 'model-limitations', title: '7. AI & ML Model Limitations', icon: Cpu },
  { id: 'data-usage', title: '8. Data Usage & Ownership', icon: Database },
  { id: 'intellectual-property', title: '9. Intellectual Property', icon: Building },
  { id: 'third-party', title: '10. Third-Party Services', icon: ExternalLink },
  { id: 'availability', title: '11. Service Availability & SLA', icon: RefreshCw },
  { id: 'liability', title: '12. Limitation of Liability', icon: ShieldAlert },
  { id: 'security', title: '13. Security & Safe Harbor', icon: Lock },
  { id: 'changes', title: '14. Changes to Terms', icon: RefreshCw },
  { id: 'contact', title: '15. Contact Information', icon: HelpCircle },
];

export const TermsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('introduction');
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
                  Legal &amp; Regulatory Documentation
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/privacy"
              className="hidden sm:inline-flex items-center text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-1.5 transition-colors"
            >
              Privacy Policy &rarr;
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Hero Header */}
      <section className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 py-10 px-4 sm:px-6 lg:px-8 transition-colors">
        <div className="max-w-4xl mx-auto text-center sm:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 mb-4">
            <Scale className="w-3.5 h-3.5" />
            <span>Platform Agreement &bull; Version 1.0</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Terms &amp; Conditions
          </h1>
          <p className="mt-2 text-sm sm:text-base text-slate-600 dark:text-slate-300">
            Terms of Service governing the use of FraudShield AI real-time risk intelligence and fraud prevention platform.
          </p>
          <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span><strong>Last Updated:</strong> September 28, 2026</span>
            <span>&bull;</span>
            <span><strong>Effective Date:</strong> Immediate</span>
            <span>&bull;</span>
            <span><strong>Scope:</strong> Enterprise &amp; SaaS Workspaces</span>
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
                  to="/privacy"
                  className="flex items-center justify-between text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  <span>View Privacy Policy</span>
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </aside>

          {/* Legal Document Content */}
          <main className="lg:col-span-8 xl:col-span-9 space-y-6">
            {/* Critical Risk Disclaimer Alert Box */}
            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-card p-4 sm:p-5">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <div className="text-xs sm:text-sm text-amber-900 dark:text-amber-200">
                  <h3 className="font-bold text-amber-950 dark:text-amber-100 text-sm mb-1">
                    Crucial Risk &amp; Detection Disclaimer
                  </h3>
                  <p className="leading-relaxed">
                    FraudShield AI provides automated, probabilistic risk scoring, anomaly detection, and assistive decision-support tools.
                    <strong> FraudShield AI does not guarantee, warrant, or promise that every fraudulent transaction, financial anomaly, unauthorized intrusion, or security threat will be detected, prevented, or mitigated.</strong>
                    Operational personnel remain solely responsible for validating evidence, configuring enforcement rules, and taking final transaction decisions.
                  </p>
                </div>
              </div>
            </div>

            {/* Section 1: Introduction */}
            <Card id="introduction" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <FileText className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">1. Introduction</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Welcome to <strong>FraudShield AI</strong> (&ldquo;FraudShield&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;our&rdquo;). These Terms and Conditions (&ldquo;Terms&rdquo;) establish the legally binding agreement between FraudShield AI and the subscriber, customer organization, or individual user (&ldquo;User&rdquo;, &ldquo;Customer&rdquo;, or &ldquo;You&rdquo;) accessing our real-time cybersecurity and fraud intelligence software.
                </p>
                <p>
                  By accessing, creating an account on, or interacting with the FraudShield AI web interface, backend APIs, streaming WebSockets, machine learning inference endpoints, or investigation modules, you acknowledge that you have read, understood, and agreed to be bound by these Terms.
                </p>
              </div>
            </Card>

            {/* Section 2: Acceptance of Terms */}
            <Card id="acceptance" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Scale className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">2. Acceptance of Terms</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  If you are using FraudShield AI on behalf of an enterprise, financial institution, or merchant organization, you represent and warrant that you possess full administrative authority to bind that entity to these Terms. If you do not agree with any provision contained herein, you must immediately terminate access to the platform.
                </p>
                <p>
                  Your continued access or utilization of any component of the platform constitutes ongoing acceptance of these Terms, including any modifications published under Section 14.
                </p>
              </div>
            </Card>

            {/* Section 3: Description of Service */}
            <Card id="service-description" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Layers className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">3. Description of Service</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI is an intelligent fraud detection and risk operations platform engineered for financial transactions, card-not-present processing, identity anomaly detection, and operational case investigation. Key capabilities provided by the service include:
                </p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li><strong>Real-time Risk Scoring:</strong> High-throughput ingestion and scoring of transaction payloads with low-latency classification.</li>
                  <li><strong>Ensemble Machine Learning:</strong> Multi-model inference utilizing supervised classifiers (e.g. XGBoost), unsupervised isolation forests, and rule-based heuristic layers.</li>
                  <li><strong>Explainable AI (XAI):</strong> Local feature attribution computation using SHAP values to explain transaction anomaly drivers.</li>
                  <li><strong>Case Investigation Workspace:</strong> Centralized forensics timeline, evidence linking, alert triage, and decision recording.</li>
                  <li><strong>AI Copilot Assistance:</strong> Natural-language decision support, pattern summarization, and query execution assistance.</li>
                  <li><strong>Role-Based Access Control (RBAC):</strong> Multi-tenant isolation with granular permission sets (Fraud Analyst, Risk Manager, Admin, Viewer).</li>
                </ul>
              </div>
            </Card>

            {/* Section 4: User Responsibilities */}
            <Card id="user-responsibilities" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <ShieldCheck className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">4. User Responsibilities &amp; Acceptable Use</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  As an authorized user of FraudShield AI, you agree to:
                </p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li>Utilize the platform solely for lawful fraud detection, cybersecurity monitoring, and transaction integrity purposes.</li>
                  <li>Provide accurate, genuine input telemetry and not intentionally ingest corrupt, fabricated, or deceptive data designed to bypass detection filters.</li>
                  <li>Refrain from reverse engineering, decompiling, disassembling, or extracting the weights or underlying model schemas of the proprietary ML engine.</li>
                  <li>Refrain from launching denial-of-service (DoS) attacks, brute-force requests, unauthorized penetration tests, or automated crawlers against production endpoints.</li>
                  <li>Promptly notify the organization&rsquo;s security administrator upon discovery of any credential breach, vulnerability, or anomaly in access permissions.</li>
                </ul>
              </div>
            </Card>

            {/* Section 5: Account & Authentication */}
            <Card id="account-auth" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Lock className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">5. Account &amp; Authentication</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Access to the FraudShield AI console requires credential authentication generating JSON Web Tokens (JWT). Users are strictly prohibited from sharing login credentials, session tokens, or API keys across unauthorized individuals.
                </p>
                <p>
                  Administrators are responsible for assigning appropriate RBAC privileges to staff members based on the principle of least privilege. FraudShield AI reserves the right to suspend or revoke tokens associated with suspicious or unauthorized activity.
                </p>
              </div>
            </Card>

            {/* Section 6: Fraud & Risk Disclaimer */}
            <Card id="fraud-disclaimer" className="scroll-mt-24 border-amber-200 dark:border-amber-800">
              <div className="flex items-center gap-2.5 mb-3 text-amber-600 dark:text-amber-400">
                <AlertTriangle className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">6. Fraud &amp; Risk Detection Disclaimer</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p className="font-semibold text-slate-800 dark:text-slate-200">
                  IMPORTANT: FraudShield AI is a software-assisted risk analytics and alert triage solution.
                </p>
                <p>
                  FraudShield AI makes no guarantees, warranties, representations, or covenants that the software will identify 100% of unauthorized activities, fraud syndicates, credential stuffing attempts, money laundering patterns, or malicious transactions. Risk scores (0&ndash;100) are probabilistic estimations based upon available input features, historical calibration datasets, and configured heuristic thresholds.
                </p>
                <p>
                  The platform is designed to assist human analysts and automated risk pipelines, but final operational determinations (including approving, flagging, freezing, or declining financial transactions) remain the sole responsibility and liability of the operating enterprise.
                </p>
              </div>
            </Card>

            {/* Section 7: AI & ML Model Limitations */}
            <Card id="model-limitations" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Cpu className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">7. AI &amp; ML Model Limitations</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Machine learning models operate under inherent technical constraints that users must understand:
                </p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li><strong>False Positives &amp; False Negatives:</strong> Statistical models may occasionally classify legitimate transactions as high-risk (false positive) or fail to flag novel adversarial evasion vectors (false negative).</li>
                  <li><strong>Concept &amp; Data Drift:</strong> Changes in macro consumer behavior or merchant patterns over time may affect scoring accuracy until models are recalibrated or retrained.</li>
                  <li><strong>Generative AI &amp; Copilot Summaries:</strong> Generative AI features (e.g. LLM-based case summarization) are assistive tools. Users must independently verify investigative assertions, generated explanations, and regulatory filing notes against source audit evidence.</li>
                </ul>
              </div>
            </Card>

            {/* Section 8: Data Usage */}
            <Card id="data-usage" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Database className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">8. Data Usage &amp; Ownership</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  Customers retain full proprietary ownership of all transaction payloads, customer records, and operational notes ingested into FraudShield AI.
                </p>
                <p>
                  FraudShield AI processes customer data strictly for the purposes of executing fraud scoring, populating forensic investigation timelines, generating audit logs, and delivering requested platform features. FraudShield AI does not sell or distribute customer transaction records to unaffiliated third parties.
                </p>
              </div>
            </Card>

            {/* Section 9: Intellectual Property */}
            <Card id="intellectual-property" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Building className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">9. Intellectual Property</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  All rights, titles, and interests in FraudShield AI—including but not limited to the user interface designs, visual components, proprietary scoring algorithms, orchestration logic, documentation, logos, and software code—remain the exclusive intellectual property of FraudShield AI.
                </p>
                <p>
                  Users receive a limited, revocable, non-exclusive, non-transferable license to access and use the platform in accordance with their designated subscription or deployment tier.
                </p>
              </div>
            </Card>

            {/* Section 10: Third-Party Services */}
            <Card id="third-party" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <ExternalLink className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">10. Third-Party Services &amp; Integrations</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI may offer optional integrations with third-party service providers, including cloud hosting providers, external database drivers, or third-party LLM API providers for assistive copilot capabilities.
                </p>
                <p>
                  FraudShield AI is not responsible for the uptime, operational policies, or data handling practices of third-party external services outside our direct control.
                </p>
              </div>
            </Card>

            {/* Section 11: Service Availability & SLA */}
            <Card id="availability" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <RefreshCw className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">11. Service Availability &amp; Modifications</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI strives to maintain high availability and real-time responsiveness. However, the platform is provided on an &ldquo;AS IS&rdquo; and &ldquo;AS AVAILABLE&rdquo; basis.
                </p>
                <p>
                  We reserve the right to perform scheduled maintenance, apply security patches, deploy model upgrades, or modify platform features with prior notice where practicable. FraudShield AI does not warrant uninterrupted or error-free continuous service.
                </p>
              </div>
            </Card>

            {/* Section 12: Limitation of Liability */}
            <Card id="liability" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-red-600 dark:text-red-400">
                <ShieldAlert className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">12. Limitation of Liability</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  To the maximum extent permitted under applicable law, in no event shall FraudShield AI, its developers, affiliates, directors, or contributors be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation:
                </p>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li>Direct or indirect financial losses arising from fraudulent transactions or chargebacks.</li>
                  <li>Loss of revenue, business interruption, or loss of profits resulting from system downtime or false positive transaction declines.</li>
                  <li>Decisions made or actions taken by the user or customer based on model scores, copilot insights, or risk classifications.</li>
                </ul>
                <p>
                  Total cumulative liability for all claims arising under these Terms shall be limited to the amount paid by the customer to FraudShield AI in the preceding twelve (12) months.
                </p>
              </div>
            </Card>

            {/* Section 13: Security & Safe Harbor */}
            <Card id="security" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <Lock className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">13. Security &amp; Vulnerability Reporting</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI incorporates technical safeguards, including TLS transit encryption, password hashing, parameterized database queries, and Row-Level Security isolation.
                </p>
                <p>
                  Security researchers and users discovering potential vulnerabilities are encouraged to disclose findings responsibly to our security desk at <span className="font-mono text-blue-600 dark:text-blue-400">security@fraudshield.ai</span>. FraudShield AI supports safe harbor for good-faith vulnerability reporting adhering to coordinated disclosure standards.
                </p>
              </div>
            </Card>

            {/* Section 14: Changes to Terms */}
            <Card id="changes" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <RefreshCw className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">14. Changes to Terms</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  FraudShield AI reserves the right to revise or update these Terms periodically to reflect platform enhancements, operational changes, or legal requirements.
                </p>
                <p>
                  When changes occur, the &ldquo;Last Updated&rdquo; date at the top of this document will be updated. Continued use of the platform after revised terms are posted constitutes binding agreement to the updated Terms.
                </p>
              </div>
            </Card>

            {/* Section 15: Contact Information */}
            <Card id="contact" className="scroll-mt-24">
              <div className="flex items-center gap-2.5 mb-3 text-blue-600 dark:text-blue-400">
                <HelpCircle className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">15. Contact Information</h2>
              </div>
              <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
                <p>
                  For inquiries regarding these Terms and Conditions, platform compliance, or licensing agreements, please contact the FraudShield AI team:
                </p>
                <div className="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-btn border border-slate-200 dark:border-slate-700 space-y-1 font-mono text-xs">
                  <p><span className="text-slate-500 dark:text-slate-400">Legal Desk:</span> legal@fraudshield.ai</p>
                  <p><span className="text-slate-500 dark:text-slate-400">Security Office:</span> security@fraudshield.ai</p>
                  <p><span className="text-slate-500 dark:text-slate-400">Platform Support:</span> support@fraudshield.ai</p>
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

export default TermsPage;
