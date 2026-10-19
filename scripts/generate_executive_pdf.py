#!/usr/bin/env python3
"""
Professional Executive PDF Generator for Axeom Challenge.
Produces an exact 2-page A4 consulting report:
- Page 1: Executive Project Overview & Business Analysis
- Page 2: System Architecture & Technical Diagrams
Utilizes clean typography, corporate color palette, and vector SVGs.
"""

import os
import subprocess
from pathlib import Path

WORKSPACE = Path("/home/arslan-tariq/Downloads/Axeom Challenge - Pack 01")
HTML_PATH = WORKSPACE / "executive_report.html"
PDF_PATH = WORKSPACE / "AXEOM_FINAL_SUBMISSION" / "Axeom_Executive_Report.pdf"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Axeom Studio — Executive Report & Technical Writeup</title>
<style>
  @page {
    size: A4 portrait;
    margin: 0;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    font-size: 8.2pt;
    line-height: 1.35;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .page {
    width: 210mm;
    height: 297mm;
    max-height: 297mm;
    padding: 10mm 12mm 8mm 12mm;
    page-break-after: always;
    overflow: hidden;
    position: relative;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .page:last-child {
    page-break-after: avoid;
  }

  /* Header Styles */
  .header {
    border-bottom: 2px solid #0f172a;
    padding-bottom: 5px;
    margin-bottom: 7px;
  }
  .header-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .title-block h1 {
    font-size: 15pt;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #0f172a;
    line-height: 1.1;
  }
  .title-block .subtitle {
    font-size: 9.5pt;
    font-weight: 600;
    color: #475569;
  }
  .title-block .desc {
    font-size: 7.5pt;
    color: #64748b;
    font-style: italic;
    margin-top: 1px;
  }
  .brand-badge {
    background: #0f172a;
    color: #ffffff;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .brand-badge span {
    color: #84cc16;
  }
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 4px 8px;
    margin-top: 5px;
    font-size: 7pt;
    gap: 4px;
  }
  .meta-item strong {
    color: #0f172a;
  }
  .meta-item a {
    color: #2563eb;
    text-decoration: none;
  }

  /* Section Styles */
  .section {
    margin-bottom: 6px;
  }
  .section-title {
    font-size: 8.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #0f172a;
    border-left: 3px solid #84cc16;
    padding-left: 5px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .section-title span.badge {
    font-size: 6.5pt;
    background: #e2e8f0;
    color: #334155;
    padding: 1px 5px;
    border-radius: 3px;
    text-transform: none;
    font-weight: 600;
  }

  /* Executive Summary */
  .summary-text {
    font-size: 7.8pt;
    color: #334155;
    text-align: justify;
    line-height: 1.35;
  }

  /* KPI Cards */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 5px;
  }
  .kpi-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px 5px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: #84cc16;
  }
  .kpi-card.alert::before {
    background: #ef4444;
  }
  .kpi-card.warn::before {
    background: #f59e0b;
  }
  .kpi-label {
    font-size: 6.5pt;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.2px;
    margin-bottom: 1px;
  }
  .kpi-val {
    font-size: 9.5pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
  }
  .kpi-sub {
    font-size: 6pt;
    color: #64748b;
    margin-top: 1px;
  }

  /* Tables */
  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 7pt;
    line-height: 1.25;
  }
  .data-table th, .data-table td {
    padding: 3px 5px;
    border: 1px solid #e2e8f0;
    vertical-align: top;
  }
  .data-table th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    font-size: 6.8pt;
    text-transform: uppercase;
  }
  .data-table td.dim {
    font-weight: 700;
    color: #0f172a;
    white-space: nowrap;
    background: #f8fafc;
  }
  .data-table td.ev {
    color: #475569;
    font-size: 6.8pt;
  }
  .data-table td.res {
    color: #1e293b;
  }

  /* Two Column Layout */
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .card-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 4px 7px;
  }
  .card-box h4 {
    font-size: 7.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
  }
  .card-box ul {
    list-style: none;
    padding-left: 0;
  }
  .card-box li {
    font-size: 6.8pt;
    color: #334155;
    position: relative;
    padding-left: 8px;
    margin-bottom: 2px;
    line-height: 1.25;
  }
  .card-box li::before {
    content: "•";
    position: absolute;
    left: 0;
    color: #84cc16;
    font-weight: bold;
  }

  /* Jev Limitation Notice */
  .notice-box {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 3px solid #f59e0b;
    border-radius: 3px;
    padding: 3px 6px;
    font-size: 6.8pt;
    color: #92400e;
    line-height: 1.3;
  }
  .notice-box strong {
    color: #b45309;
  }

  /* Next Two Weeks */
  .roadmap-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
  }
  .roadmap-card {
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    padding: 3px 5px;
    background: #ffffff;
  }
  .roadmap-card h5 {
    font-size: 7pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 1px;
    display: flex;
    justify-content: space-between;
  }
  .roadmap-card h5 span {
    font-size: 6pt;
    color: #84cc16;
    font-weight: 800;
  }
  .roadmap-card p {
    font-size: 6.5pt;
    color: #475569;
    line-height: 1.2;
  }

  /* Footer */
  .footer {
    border-top: 1px solid #e2e8f0;
    padding-top: 3px;
    display: flex;
    justify-content: space-between;
    font-size: 6.5pt;
    color: #94a3b8;
    margin-top: 3px;
  }

  /* Page 2 Diagram Containers */
  .diagram-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 5px;
    margin-bottom: 7px;
  }
  .diagram-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }
  .diagram-header h3 {
    font-size: 8.2pt;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .diagram-header h3::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #84cc16;
    border-radius: 50%;
  }
  .diagram-tag {
    font-size: 6.5pt;
    color: #64748b;
    background: #f1f5f9;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 600;
  }
  svg {
    display: block;
    width: 100%;
    height: auto;
  }
</style>
</head>
<body>

<!-- ======================================================== -->
<!-- PAGE 1: EXECUTIVE PROJECT OVERVIEW & BUSINESS ANALYSIS   -->
<!-- ======================================================== -->
<div class="page" id="page-1">
  <div>
    <!-- Header -->
    <div class="header">
      <div class="header-top">
        <div class="title-block">
          <h1>AXEOM STUDIO</h1>
          <div class="subtitle">Business Intelligence & Operations Operating System</div>
          <div class="desc">Evidence-Based Financial Reconciliation, Client Intelligence & Operational Decision Support</div>
        </div>
        <div class="brand-badge">
          AXEOM <span>OS</span> • PACK 01
        </div>
      </div>
      <div class="meta-grid">
        <div class="meta-item"><strong>Candidate:</strong> Arslan Tariq (tsa6648@gmail.com)</div>
        <div class="meta-item"><strong>Reference Date:</strong> October 6, 2026 (Pack 01)</div>
        <div class="meta-item"><strong>Live System:</strong> <a href="https://axeom-business-intelligence.vercel.app">axeom-business-intelligence.vercel.app</a></div>
        <div class="meta-item"><strong>Repository:</strong> <a href="https://github.com/arslantariq364/axeom-business-intelligence">github.com/arslantariq364/axeom...</a></div>
      </div>
    </div>

    <!-- Section 1: Executive Summary -->
    <div class="section">
      <div class="section-title">
        1. Executive Summary
        <span class="badge">Problem & Scope</span>
      </div>
      <p class="summary-text">
        Axeom Studio operates a commercial video content production business whose financial reality and operational delivery were severely obscured by disconnected software tools and unlinked multi-channel communication (Email, WhatsApp, Instagram, Voice Notes). Discrepancies between billing ledgers and actual bank receipts left the owner blind to true accounts receivable, unrecognized credits, and completed client shoots that were never invoiced. By programmatically cross-auditing bank payment receipts, booking logs, and message records across 1,112 rows of raw source data, we restored empirical clarity. We engineered a high-reliability, mobile-first operations dashboard deployed on Vercel serverless edge with Neon PostgreSQL, giving the owner zero-latency triage over delinquent accounts, unbilled revenue, and high-risk client churn.
      </p>
    </div>

    <!-- Section 2: Key Business Findings (KPI Cards) -->
    <div class="section">
      <div class="section-title">
        2. Verified Business Findings & Financial Truth
        <span class="badge">Audit Date: 2026-10-06</span>
      </div>
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Canonical Clients</div>
          <div class="kpi-val">29</div>
          <div class="kpi-sub">0 False Merges • 1 Payer</div>
        </div>
        <div class="kpi-card alert">
          <div class="kpi-label">Overdue Debt</div>
          <div class="kpi-val">$9,250.00</div>
          <div class="kpi-sub">9 Invoices Due ≤ Oct 6</div>
        </div>
        <div class="kpi-card warn">
          <div class="kpi-label">We Owe Clients</div>
          <div class="kpi-val">$2,400.00</div>
          <div class="kpi-sub">1 Credit • 1 Overpayment</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Unbilled Work</div>
          <div class="kpi-val">$2,950.00</div>
          <div class="kpi-sub">3 Completed Shoots</div>
        </div>
        <div class="kpi-card alert">
          <div class="kpi-label">Lost Requests</div>
          <div class="kpi-val">33</div>
          <div class="kpi-sub">Worsened in Aug 2026</div>
        </div>
        <div class="kpi-card warn">
          <div class="kpi-label">Unreplied Leads</div>
          <div class="kpi-val">22</div>
          <div class="kpi-sub">18 True New Prospects</div>
        </div>
      </div>
    </div>

    <!-- Section 3: Evidence & Analysis -->
    <div class="section">
      <div class="section-title">
        3. Evidence Synthesis & Analytical Methodology
        <span class="badge">Cross-Ledger Reconciliation</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 17%;">Business Question</th>
            <th style="width: 38%;">Evidence Source & Signals</th>
            <th style="width: 45%;">Finding & Deterministic Methodology</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="dim">Client Identity</td>
            <td class="ev">Multi-attribute linkage across <code>bookings</code>, <code>invoices</code>, <code>leads</code>, emails, and phone numbers.</td>
            <td class="res">Resolved <strong>29 canonical clients</strong>. Preserved distinct homonyms (Lone Star Realty vs. Lonestar Realty Group). Merged confirmed rebrands (Elevate Fitness &rarr; Athletics via email 2026-08-01). Isolated third-party payer Brightline Marketing.</td>
          </tr>
          <tr>
            <td class="dim">Financial Truth</td>
            <td class="ev">Cross-audit of bank deposits (<code>payments.csv</code>) vs. billing ledger (<code>invoices.csv</code>).</td>
            <td class="res">Reconciled <strong>$9,250.00</strong> in real client debt across 9 overdue invoices. Proved <strong>6 billing tool software errors</strong> where software falsely said unpaid but bank receipts proved full settlement (including $900 wire P5110).</td>
          </tr>
          <tr>
            <td class="dim">Unbilled Work</td>
            <td class="ev">Completed chargeable bookings (<code>bookings.csv</code>) with missing invoice references.</td>
            <td class="res">Identified <strong>$2,950.00</strong> in earned, unbilled work: DFW Founders B136 ($550), Ironclad Gym B123 ($900), Vega Auto Detailing B144 ($1,500). Preserved B023 ($0 retainer shoot for Apex Physical Therapy). Reconciled We Owe ($2,400): Lone Star credit ($1,500) and Glow double-payment ($900).</td>
          </tr>
          <tr>
            <td class="dim">Lost Requests</td>
            <td class="ev">208 multi-channel messages (<code>messages.txt</code>) audited against <code>production_board.csv</code>.</td>
            <td class="res">Flagged <strong>33 missed edit requests</strong> where <code>notes_on_board</code> remained blank. Breakdown accelerated in <strong>August 2026</strong> (12 missed) and September (16 missed) due to volume scaling and editor turnover without centralized ticketing.</td>
          </tr>
          <tr>
            <td class="dim">Churn Risk</td>
            <td class="ev">Unanswered contract inquiries (L097, Oct 2 email), branding complaints, withheld invoice.</td>
            <td class="res"><strong>Patel Insurance Group</strong> ($2,500/mo retainer) is #1 churn risk. Multiple heated complaints regarding compliance branding errors were ignored, and INV-1122 is withheld. Mirrors Meridian Wealth churn. Immediate owner phone call required.</td>
          </tr>
          <tr>
            <td class="dim">Marketing</td>
            <td class="ev">Lead channels in <code>leads.csv</code> vs. direct shoot labor and studio space in <code>costs.csv</code>.</td>
            <td class="res"><strong>Website form</strong> produced scalable inbound acquisition ($12,428.90 direct gross profit, 62.3% margin, 45% conversion); <strong>Referral</strong> had highest conversion (71.4%) and cash per account ($22,800). <em>Critical Caveat:</em> Data omits digital ad spend; represents gross contribution, not net marketing ROI.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Section 4: Implemented Technical Solution -->
    <div class="section">
      <div class="section-title">
        4. Implemented Technical Solution & Architecture
        <span class="badge">Production Vercel & Neon</span>
      </div>
      <p class="summary-text">
        The application is architected as a lightweight, mobile-first Single-Page Application powered by a <strong>Python Flask 3.1 WSGI core</strong> hosted on <strong>Vercel Serverless Edge</strong> (<code>api/index.py</code>) and backed by <strong>Neon Serverless PostgreSQL</strong> (AWS us-east-2) with PgBouncer connection pooling and isolated database branching (<code>main</code> for production, <code>dev</code> for QA). A unified idempotent ingestion engine (<code>services/ingest.py</code>) validates CSV/TXT uploads via cryptographic SHA-256 deduplication, content-based schema auto-sniffing, and atomic transaction staging. An owner-controlled Action Protocol features pre-drafted call scripts and emails requiring explicit approval (Approve, Defer, Reject), logging decisions to a durable PostgreSQL audit trail without dangerous automated outbound side-effects.
      </p>
    </div>

    <!-- Section 5: Jev Access Limitation Notice -->
    <div class="section">
      <div class="notice-box">
        <strong>Jev API Access: Not Obtained.</strong> The required Typesafe AI Jev API access was not obtained during the challenge timeframe. Consequently, live Jev integration and live model evaluations could not be completed. A deterministic rule-based classifier was implemented in <code>services/requests.py</code> as a standalone fallback for client message categorization (intent classification across edit requests, complaints, billing questions, and leads). Zero claims of live Jev accuracy are made, clearly separating intended AI scope from the independently verified fallback.
      </div>
    </div>

    <!-- Section 6: Operating Costs & Limitations -->
    <div class="section">
      <div class="two-col">
        <div class="card-box">
          <h4>Operating Costs & Infrastructure</h4>
          <ul>
            <li><strong>Vercel Edge Functions:</strong> $0.00/mo (Current Hobby tier; production ready).</li>
            <li><strong>Neon Serverless PostgreSQL:</strong> $0.00/mo (Free tier, pooled storage & compute).</li>
            <li><strong>Estimated Production Scale:</strong> ~$20–$40/mo at 50,000 monthly active requests.</li>
          </ul>
        </div>
        <div class="card-box">
          <h4>Known System & Data Limitations</h4>
          <ul>
            <li><strong>Jev Access:</strong> Live Typesafe AI API evaluation pending credential access.</li>
            <li><strong>Ad Spend Omission:</strong> Source <code>costs.csv</code> lacks digital ad spend (Meta/Google).</li>
            <li><strong>Verbal Agreements:</strong> Unrecorded phone calls or in-person studio talks omitted.</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Section 7: Next Two Weeks -->
    <div class="section" style="margin-bottom: 0;">
      <div class="section-title">
        5. Next Two Weeks Operational Roadmap
        <span class="badge">Continuous Delivery</span>
      </div>
      <div class="roadmap-grid">
        <div class="roadmap-card">
          <h5>Week 1: Data Hardening <span>W1</span></h5>
          <p>Add automated schema anomaly detection and ingestion guards for newly uploaded bank CSV exports.</p>
        </div>
        <div class="roadmap-card">
          <h5>Week 2: AI Intent Provisioning <span>W2</span></h5>
          <p>Pursue Typesafe AI credentials, benchmark Jev against deterministic baseline, and test webhook triggers.</p>
        </div>
        <div class="roadmap-card">
          <h5>Future: Ledger Sync & CRM <span>FUTURE</span></h5>
          <p>Implement bi-directional QuickBooks/Xero sync and multi-channel webhook ingestion for WhatsApp API.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Page 1 Footer -->
  <div class="footer">
    <span>Axeom Challenge (Pack 01) — Executive Report & Technical Writeup</span>
    <span>Candidate: Arslan Tariq (tsa6648@gmail.com)</span>
    <span>Page 1 of 2</span>
  </div>
</div>


<!-- ======================================================== -->
<!-- PAGE 2: SYSTEM ARCHITECTURE & TECHNICAL DIAGRAMS         -->
<!-- ======================================================== -->
<div class="page" id="page-2">
  <div>
    <!-- Header -->
    <div class="header">
      <div class="header-top">
        <div class="title-block">
          <h1>SYSTEM ARCHITECTURE & OPERATIONAL DATA FLOW</h1>
          <div class="subtitle">End-to-End Technical Topology, Idempotent Pipeline & Owner Decision Workflow</div>
        </div>
        <div class="brand-badge">
          AXEOM <span>TECH</span> • DIAGRAMS
        </div>
      </div>
    </div>

    <!-- Diagram 1: Layered System Architecture -->
    <div class="diagram-container">
      <div class="diagram-header">
        <h3>Diagram 1: Layered System Topology & Service Decomposition</h3>
        <span class="diagram-tag">Vercel Serverless Edge + Neon Cloud PostgreSQL</span>
      </div>
      <svg viewBox="0 0 740 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gradNavy" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#1e293b"/>
            <stop offset="100%" stop-color="#0f172a"/>
          </linearGradient>
          <linearGradient id="gradLime" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f7fee7"/>
            <stop offset="100%" stop-color="#ecfccb"/>
          </linearGradient>
          <linearGradient id="gradBlue" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f0f9ff"/>
            <stop offset="100%" stop-color="#e0f2fe"/>
          </linearGradient>
          <linearGradient id="gradSlate" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f8fafc"/>
            <stop offset="100%" stop-color="#f1f5f9"/>
          </linearGradient>
          <marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 8 5 L 0 9 z" fill="#475569"/>
          </marker>
          <marker id="arrLime" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 8 5 L 0 9 z" fill="#65a30d"/>
          </marker>
        </defs>

        <!-- Layer 1: Client Devices -->
        <rect x="10" y="8" width="720" height="34" rx="4" fill="url(#gradSlate)" stroke="#cbd5e1" stroke-width="1"/>
        <text x="25" y="28" font-size="9" font-weight="bold" fill="#0f172a">USER INTERFACE</text>
        <rect x="135" y="14" width="180" height="22" rx="3" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
        <text x="145" y="29" font-size="8" fill="#1e293b">Mobile Browser (390×844) [10-Sec Test]</text>
        <rect x="330" y="14" width="185" height="22" rx="3" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
        <text x="340" y="29" font-size="8" fill="#1e293b">Desktop Browser (1920×1080 Command Center)</text>
        <rect x="530" y="14" width="185" height="22" rx="3" fill="url(#gradLime)" stroke="#84cc16" stroke-width="1"/>
        <text x="545" y="29" font-size="8" font-weight="bold" fill="#365314">Zero-Login Secure URL Access</text>

        <!-- Arrow Down to Hosting -->
        <line x1="370" y1="42" x2="370" y2="52" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Layer 2: Vercel Edge Hosting -->
        <rect x="10" y="52" width="720" height="28" rx="4" fill="url(#gradNavy)" stroke="#0f172a" stroke-width="1"/>
        <text x="25" y="70" font-size="9" font-weight="bold" fill="#ffffff">VERCEL EDGE</text>
        <text x="140" y="70" font-size="8" fill="#93c5fd">HTTPS Termination • Static Asset CDN • vercel.json Rewrites • Serverless WSGI Handler (api/index.py)</text>

        <!-- Arrow Down to Backend Core -->
        <line x1="370" y1="80" x2="370" y2="90" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Layer 3: Application Core & Services -->
        <rect x="10" y="90" width="720" height="52" rx="4" fill="url(#gradBlue)" stroke="#bae6fd" stroke-width="1"/>
        <text x="25" y="108" font-size="9" font-weight="bold" fill="#0369a1">FLASK 3.1 CORE</text>
        
        <!-- Service Boxes -->
        <rect x="110" y="97" width="90" height="38" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="1"/>
        <text x="118" y="112" font-size="7.5" font-weight="bold" fill="#0c4a6e">Ingest Engine</text>
        <text x="118" y="126" font-size="6.5" fill="#475569">SHA-256 • Staging</text>

        <rect x="207" y="97" width="95" height="38" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="1"/>
        <text x="214" y="112" font-size="7.5" font-weight="bold" fill="#0c4a6e">Identity Service</text>
        <text x="214" y="126" font-size="6.5" fill="#475569">Multi-signal Linkage</text>

        <rect x="309" y="97" width="95" height="38" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="1"/>
        <text x="317" y="112" font-size="7.5" font-weight="bold" fill="#0c4a6e">Finance Audit</text>
        <text x="317" y="126" font-size="6.5" fill="#475569">Aging • Bank FIFO</text>

        <rect x="411" y="97" width="98" height="38" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="1"/>
        <text x="418" y="112" font-size="7.5" font-weight="bold" fill="#0c4a6e">Requests & Leads</text>
        <text x="418" y="126" font-size="6.5" fill="#475569">Multi-channel Audit</text>

        <rect x="516" y="97" width="102" height="38" rx="3" fill="url(#gradLime)" stroke="#84cc16" stroke-width="1"/>
        <text x="522" y="112" font-size="7.5" font-weight="bold" fill="#365314">Decision Protocol</text>
        <text x="522" y="126" font-size="6.5" fill="#4d7c0f">Scripts & Audit Log</text>

        <rect x="625" y="97" width="98" height="38" rx="3" fill="#fef2f2" stroke="#f87171" stroke-width="1" stroke-dasharray="2,2"/>
        <text x="630" y="111" font-size="7" font-weight="bold" fill="#991b1b">AI Classifier</text>
        <text x="630" y="122" font-size="6" fill="#b91c1c">Fallback: Rule-based</text>
        <text x="630" y="131" font-size="5.5" font-weight="bold" fill="#dc2626">Jev: Not Connected</text>

        <!-- Arrow Down to Persistence -->
        <line x1="370" y1="142" x2="370" y2="152" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Layer 4: Persistence & Outputs -->
        <rect x="10" y="152" width="720" height="40" rx="4" fill="url(#gradSlate)" stroke="#cbd5e1" stroke-width="1"/>
        <text x="25" y="176" font-size="9" font-weight="bold" fill="#0f172a">PERSISTENCE</text>
        
        <rect x="135" y="158" width="260" height="28" rx="3" fill="#ffffff" stroke="#64748b" stroke-width="1"/>
        <text x="145" y="172" font-size="7.5" font-weight="bold" fill="#0f172a">Neon PostgreSQL (Production AWS us-east-2)</text>
        <text x="145" y="182" font-size="6.5" fill="#64748b">PgBouncer Connection Pooling • Branching (main / dev)</text>

        <rect x="405" y="158" width="150" height="28" rx="3" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
        <text x="415" y="172" font-size="7.5" font-weight="bold" fill="#0f172a">SQLite Fallback</text>
        <text x="415" y="182" font-size="6.5" fill="#64748b">Zero-Network Offline Tests</text>

        <rect x="565" y="158" width="155" height="28" rx="3" fill="url(#gradLime)" stroke="#84cc16" stroke-width="1"/>
        <text x="575" y="172" font-size="7.5" font-weight="bold" fill="#365314">Zero-Disk Stream Output</text>
        <text x="575" y="182" font-size="6.5" fill="#4d7c0f">Live answers.json & Reports</text>
      </svg>
    </div>

    <!-- Diagram 2: Data Processing Pipeline -->
    <div class="diagram-container">
      <div class="diagram-header">
        <h3>Diagram 2: Idempotent Data Ingestion & Multi-File Reconciliation Pipeline</h3>
        <span class="diagram-tag">Automated Content-Based Schema Sniffing & Atomic Staging</span>
      </div>
      <svg viewBox="0 0 740 160" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gradStep" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="100%" stop-color="#f8fafc"/>
          </linearGradient>
        </defs>

        <!-- Pipeline Nodes -->
        <!-- Node 1 -->
        <rect x="10" y="25" width="85" height="52" rx="4" fill="url(#gradStep)" stroke="#0f172a" stroke-width="1.2"/>
        <text x="18" y="44" font-size="8" font-weight="bold" fill="#0f172a">1. Raw Files</text>
        <text x="18" y="58" font-size="6.5" fill="#475569">CSV Exports &amp;</text>
        <text x="18" y="68" font-size="6.5" fill="#475569">messages.txt</text>
        
        <line x1="95" y1="51" x2="115" y2="51" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Node 2 -->
        <rect x="115" y="25" width="95" height="52" rx="4" fill="url(#gradStep)" stroke="#0f172a" stroke-width="1.2"/>
        <text x="123" y="44" font-size="8" font-weight="bold" fill="#0f172a">2. Validation</text>
        <text x="123" y="58" font-size="6.5" fill="#475569">Encoding Check</text>
        <text x="123" y="68" font-size="6.5" fill="#475569">Payload &lt; 16MB</text>

        <!-- Error Branch Down -->
        <line x1="162" y1="77" x2="162" y2="110" stroke="#ef4444" stroke-width="1.5" marker-end="url(#arr)"/>
        <rect x="115" y="110" width="130" height="38" rx="4" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>
        <text x="123" y="125" font-size="7.5" font-weight="bold" fill="#991b1b">Rejection Engine</text>
        <text x="123" y="137" font-size="6.5" fill="#b91c1c">Invalid Header / Type Error Modal</text>

        <line x1="210" y1="51" x2="230" y2="51" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Node 3 -->
        <rect x="230" y="25" width="95" height="52" rx="4" fill="url(#gradStep)" stroke="#0f172a" stroke-width="1.2"/>
        <text x="238" y="44" font-size="8" font-weight="bold" fill="#0f172a">3. Schema Sniff</text>
        <text x="238" y="58" font-size="6.5" fill="#475569">Header Matcher</text>
        <text x="238" y="68" font-size="6.5" fill="#475569">Detect Role/Table</text>

        <line x1="325" y1="51" x2="345" y2="51" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Node 4 -->
        <rect x="345" y="25" width="95" height="52" rx="4" fill="url(#gradStep)" stroke="#0f172a" stroke-width="1.2"/>
        <text x="353" y="44" font-size="8" font-weight="bold" fill="#0f172a">4. SHA-256 Check</text>
        <text x="353" y="58" font-size="6.5" fill="#475569">Deduplication</text>
        <text x="353" y="68" font-size="6.5" fill="#475569">Skip Duplicate File</text>

        <line x1="440" y1="51" x2="460" y2="51" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Node 5 -->
        <rect x="460" y="25" width="105" height="52" rx="4" fill="url(#gradStep)" stroke="#0f172a" stroke-width="1.2"/>
        <text x="468" y="44" font-size="8" font-weight="bold" fill="#0f172a">5. Entity Linkage</text>
        <text x="468" y="58" font-size="6.5" fill="#475569">Canonical Matching</text>
        <text x="468" y="68" font-size="6.5" fill="#475569">Phone/Email Domain</text>

        <line x1="565" y1="51" x2="585" y2="51" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Node 6 -->
        <rect x="585" y="25" width="145" height="52" rx="4" fill="url(#gradLime)" stroke="#84cc16" stroke-width="1.5"/>
        <text x="595" y="44" font-size="8.5" font-weight="bold" fill="#365314">6. Reconciled Outputs</text>
        <text x="595" y="58" font-size="7" fill="#4d7c0f">Durable Ledger Mutations</text>
        <text x="595" y="69" font-size="7" font-weight="bold" fill="#15803d">Dynamic UI &amp; answers.json</text>

        <!-- Pipeline Legend -->
        <rect x="280" y="110" width="450" height="38" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
        <text x="290" y="125" font-size="7.5" font-weight="bold" fill="#0f172a">Pipeline Guarantees &amp; Safety:</text>
        <text x="290" y="137" font-size="6.5" fill="#475569">Atomic Transaction Rollback (BEGIN...COMMIT) • Baseline Canonical Clients C01–C29 Protected Against Deletion</text>
      </svg>
    </div>

    <!-- Diagram 3: Owner Decision Workflow -->
    <div class="diagram-container" style="margin-bottom: 0;">
      <div class="diagram-header">
        <h3>Diagram 3: Owner Decision & Priority Action Protocol</h3>
        <span class="diagram-tag">Safety-First Protocol: Zero Uncontrolled External Side-Effects</span>
      </div>
      <svg viewBox="0 0 740 170" xmlns="http://www.w3.org/2000/svg">
        <!-- Stage 1 -->
        <rect x="10" y="30" width="115" height="55" rx="4" fill="#f8fafc" stroke="#64748b" stroke-width="1.2"/>
        <text x="18" y="50" font-size="8" font-weight="bold" fill="#0f172a">1. Evidence Ingestion</text>
        <text x="18" y="64" font-size="6.5" fill="#475569">• Overdue Receivables</text>
        <text x="18" y="74" font-size="6.5" fill="#475569">• Ignored Inbound Leads</text>

        <line x1="125" y1="57" x2="145" y2="57" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Stage 2 -->
        <rect x="145" y="30" width="115" height="55" rx="4" fill="#f8fafc" stroke="#64748b" stroke-width="1.2"/>
        <text x="153" y="50" font-size="8" font-weight="bold" fill="#0f172a">2. Risk Scoring</text>
        <text x="153" y="64" font-size="6.5" fill="#475569">• Retainer Churn Risk</text>
        <text x="153" y="74" font-size="6.5" fill="#475569">• Days Overdue Aging</text>

        <line x1="260" y1="57" x2="280" y2="57" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Stage 3 -->
        <rect x="280" y="30" width="125" height="55" rx="4" fill="url(#gradLime)" stroke="#84cc16" stroke-width="1.5"/>
        <text x="288" y="50" font-size="8" font-weight="bold" fill="#365314">3. Hero Action Card</text>
        <text x="288" y="64" font-size="6.5" fill="#4d7c0f">• Pre-drafted Call Script</text>
        <text x="288" y="74" font-size="6.5" fill="#4d7c0f">• Full Evidence Dossier</text>

        <line x1="405" y1="57" x2="425" y2="57" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Stage 4: Owner Triage Modal -->
        <rect x="425" y="15" width="125" height="85" rx="4" fill="#0f172a" stroke="#0f172a" stroke-width="1.5"/>
        <text x="435" y="34" font-size="8" font-weight="bold" fill="#ffffff">4. Owner Review</text>
        
        <!-- Options inside Modal -->
        <rect x="435" y="42" width="105" height="15" rx="2" fill="#15803d"/>
        <text x="455" y="53" font-size="6.5" font-weight="bold" fill="#ffffff">Approve (Execute)</text>

        <rect x="435" y="60" width="105" height="15" rx="2" fill="#b45309"/>
        <text x="455" y="71" font-size="6.5" font-weight="bold" fill="#ffffff">Defer (Follow-up)</text>

        <rect x="435" y="78" width="105" height="15" rx="2" fill="#475569"/>
        <text x="455" y="89" font-size="6.5" font-weight="bold" fill="#ffffff">Reject (Dismiss)</text>

        <!-- Lines to Audit Trail -->
        <line x1="550" y1="50" x2="575" y2="50" stroke="#15803d" stroke-width="1.5" marker-end="url(#arrLime)"/>
        <line x1="550" y1="68" x2="575" y2="68" stroke="#b45309" stroke-width="1.5" marker-end="url(#arr)"/>
        <line x1="550" y1="86" x2="575" y2="86" stroke="#475569" stroke-width="1.5" marker-end="url(#arr)"/>

        <!-- Stage 5: Audit Trail -->
        <rect x="575" y="30" width="155" height="55" rx="4" fill="#f8fafc" stroke="#0f172a" stroke-width="1.5"/>
        <text x="585" y="48" font-size="8.5" font-weight="bold" fill="#0f172a">5. Durable Audit Trail</text>
        <text x="585" y="62" font-size="7" fill="#334155">• Decision Logged in Neon PG</text>
        <text x="585" y="73" font-size="7" fill="#334155">• Copy Script to Clipboard</text>

        <!-- Safety Banner at Bottom -->
        <rect x="10" y="115" width="720" height="32" rx="4" fill="#fefce8" stroke="#fef08a" stroke-width="1"/>
        <text x="25" y="132" font-size="7.5" font-weight="bold" fill="#854d0e">Strict Owner-Controlled Safety Protocol:</text>
        <text x="235" y="132" font-size="7" fill="#713f12">Axeom Studio NEVER dispatches unapproved emails, SMS messages, or financial ledger writes without explicit owner authorization.</text>
      </svg>
    </div>
  </div>

  <!-- Page 2 Footer -->
  <div class="footer">
    <span>Axeom Challenge (Pack 01) — Executive Report & Technical Writeup</span>
    <span>Candidate: Arslan Tariq (tsa6648@gmail.com)</span>
    <span>Page 2 of 2</span>
  </div>
</div>

</body>
</html>
"""

def generate_pdf():
    print(f"[PDF] Writing HTML markup to {HTML_PATH}...")
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print(f"[PDF] Rendering PDF via Google Chrome headless print-to-pdf...")
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={PDF_PATH}",
        str(HTML_PATH)
    ]
    subprocess.run(cmd, check=True)

    print(f"[PDF] Validating generated PDF: {PDF_PATH}...")
    # Check page count
    probe = subprocess.check_output(["pdfinfo", str(PDF_PATH)]).decode("utf-8")
    for line in probe.splitlines():
        if "Pages:" in line:
            print(f"  {line.strip()}")
            pages = int(line.split(":")[1].strip())
            assert pages == 2, f"CRITICAL: PDF page count is {pages}, expected exactly 2!"

    print(f"  ✅ PDF successfully verified with EXACTLY 2 A4 pages!")

if __name__ == "__main__":
    generate_pdf()
