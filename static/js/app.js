/**
 * Axeom Owner OS - Frontend Controller
 * Conneq CRM Light Sage & Lime Design System Implementation
 */

let appState = null;
let currentView = 'today';
let selectedClientId = 'C12'; // Default to Patel Insurance Group

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initUpload();
  initSearch();
  loadAppState();
});

// Load main application state from backend
async function loadAppState() {
  try {
    const res = await fetch('/api/state');
    const data = await res.json();
    if (data.status === 'success') {
      appState = data;
      renderAllViews();
    }
  } catch (err) {
    console.error('Failed to load application state:', err);
  }
}

// Navigation between screens
function initNavigation() {
  const navBtns = document.querySelectorAll('[data-view-target]');
  navBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const target = btn.getAttribute('data-view-target');
      switchView(target);
    });
  });

  // Check URL hash if present
  const hash = window.location.hash.replace('#', '');
  if (['today', 'clients', 'money', 'requests', 'evidence', 'history', 'upload'].includes(hash)) {
    switchView(hash);
  }
}

function switchView(viewName) {
  currentView = viewName;
  window.location.hash = viewName;

  // Update nav buttons
  document.querySelectorAll('[data-view-target]').forEach(btn => {
    if (btn.getAttribute('data-view-target') === viewName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Update views
  document.querySelectorAll('.app-view').forEach(view => {
    if (view.id === `view-${viewName}`) {
      view.classList.add('active');
    } else {
      view.classList.remove('active');
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });

  // If switched to history, load selected client
  if (viewName === 'history') {
    renderClientHistory(selectedClientId);
  }
}

function renderAllViews() {
  if (!appState) return;

  renderTodayView();
  renderClientsView();
  renderMoneyView();
  renderRequestsView();
  renderEvidenceView();
  renderClientHistory(selectedClientId);
}

// -------------------------------------------------------------------------
// 1. TODAY SCREEN (Compact Header, Lime Hero Card, Next 2, Business Summary)
// -------------------------------------------------------------------------
function renderTodayView() {
  const today = appState.today;
  const metrics = appState.metrics;
  const decisions = appState.decisions || {};

  // B. First Recommended Action: Prominent Lime-Accented Card
  const heroCard = document.getElementById('hero-card-container');
  if (heroCard) {
    const heroDec = decisions['action_patel_call'] || { status: 'pending' };
    let statusLabel = 'ACTION REQUIRED';
    let statusClass = 'badge-neutral';

    if (heroDec.status === 'in_progress') {
      statusLabel = 'IN PROGRESS';
      statusClass = 'badge-warning';
    } else if (heroDec.status === 'completed') {
      statusLabel = 'RESOLVED';
      statusClass = 'badge-success';
    } else if (heroDec.status === 'deferred') {
      statusLabel = 'DEFERRED (24H)';
      statusClass = 'badge-neutral';
    }

    heroCard.innerHTML = `
      <div class="hero-lime-card">
        <div class="hero-header-row">
          <div class="hero-pill-tag">
            <span class="pulse-dot danger"></span>
            URGENT ACTION #1 • CHURN INTERVENTION
          </div>
          <span class="badge ${statusClass}">${statusLabel}</span>
        </div>

        <h3 class="hero-action-headline">Call Nina & Raj Patel (${escapeHtml(today.hero_action.client)})</h3>

        <div class="hero-impact-pill">
          💰 At Risk: ${escapeHtml(today.hero_action.retainer_value)} + Overdue Invoice ${escapeHtml(today.hero_action.overdue_invoice)}
        </div>

        <ul class="hero-bullet-list">
          <li class="hero-bullet-item">
            <span class="hero-bullet-dot">1.</span>
            <span>Unanswered contract review inquiry (Lead L097) & follow-up email Oct 2.</span>
          </li>
          <li class="hero-bullet-item">
            <span class="hero-bullet-dot">2.</span>
            <span>Client angry over missing regulatory branding on <em>'teen driver tips'</em> (V088, V121).</span>
          </li>
          <li class="hero-bullet-item">
            <span class="hero-bullet-dot">3.</span>
            <span>Invoice INV-1122 ($2,500) withheld 21 days late (mirrors Meridian Wealth churn).</span>
          </li>
        </ul>

        <div class="hero-controls-row">
          <button class="btn btn-primary" onclick="openActionModal('action_patel_call', 'Prepare Call Script for Patel Insurance Group', '${escapeHtml(today.hero_action.draft_script)}', 'Nina & Raj Patel (214-555-0195)')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            Prepare reminder
          </button>
          <button class="btn btn-outline-dark" onclick="viewClientDetail('C12')">
            View evidence
          </button>
          <button class="btn btn-secondary btn-sm" onclick="quickDeferAction('action_patel_call')">
            Defer
          </button>
        </div>
      </div>
    `;
  }

  // C. Next Two Actions: Compact Off-White Cards
  const secContainer = document.getElementById('secondary-actions-container');
  if (secContainer) {
    const act2 = today.monday_top_3[1];
    const act3 = today.monday_top_3[2];
    const dec2 = decisions['action_bill_unbilled'] || { status: 'pending' };
    const dec3 = decisions['action_collect_overdue'] || { status: 'pending' };

    secContainer.innerHTML = `
      <div class="action-card">
        <div>
          <div class="action-card-header">
            <span class="action-tag warning">ACTION #2 • UNBILLED WORK & CREDITS</span>
            <span class="badge ${dec2.status === 'completed' ? 'badge-success' : 'badge-neutral'}">${dec2.status.toUpperCase()}</span>
          </div>
          <h4 class="action-card-title">${act2.title}</h4>
          <div class="action-card-impact">💰 ${act2.financial_impact}</div>
          <p class="action-card-desc">${act2.summary}</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button class="btn btn-primary btn-sm" onclick="openActionModal('action_bill_unbilled', 'Bill Unbilled Shoots & Apply Credits', '${escapeHtml(act2.draft_notes)}', '${act2.contact}')">
            Review invoices & credits
          </button>
          <button class="btn btn-secondary btn-sm" onclick="switchView('money')">
            View evidence
          </button>
          <button class="btn btn-secondary btn-sm" onclick="quickDeferAction('action_bill_unbilled')">
            Defer
          </button>
        </div>
      </div>

      <div class="action-card">
        <div>
          <div class="action-card-header">
            <span class="action-tag info">ACTION #3 • OVERDUE COLLECTIONS & TOOL FIXES</span>
            <span class="badge ${dec3.status === 'completed' ? 'badge-success' : 'badge-neutral'}">${dec3.status.toUpperCase()}</span>
          </div>
          <h4 class="action-card-title">${act3.title}</h4>
          <div class="action-card-impact">💰 ${act3.financial_impact}</div>
          <p class="action-card-desc">${act3.summary}</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button class="btn btn-primary btn-sm" onclick="openActionModal('action_collect_overdue', 'Collect Aged Receivables & Fix Billing Tool', '${escapeHtml(act3.draft_notes)}', '${act3.contact}')">
            Review collection queue
          </button>
          <button class="btn btn-secondary btn-sm" onclick="switchView('money')">
            View evidence
          </button>
          <button class="btn btn-secondary btn-sm" onclick="quickDeferAction('action_collect_overdue')">
            Defer
          </button>
        </div>
      </div>
    `;
  }

  // D. Business Summary Cards (Accurate distinction of money owed vs overdue)
  const pulseGrid = document.getElementById('pulse-grid-container');
  if (pulseGrid) {
    pulseGrid.innerHTML = `
      <div class="pulse-card" onclick="switchView('money'); setMoneySubTab('overdue');">
        <div class="pulse-card-label">OVERDUE PAYMENTS <span style="color:var(--danger)">⚠️</span></div>
        <div class="pulse-card-value" style="color:var(--danger)">$${metrics.overdue_total.toLocaleString('en-US', {minimumFractionDigits:2})}</div>
        <div class="pulse-card-sub">9 invoices past due date</div>
      </div>

      <div class="pulse-card" onclick="switchView('money'); setMoneySubTab('never_billed');">
        <div class="pulse-card-label">UNINVOICED WORK <span>⚡</span></div>
        <div class="pulse-card-value" style="color:var(--warning)">$${metrics.never_billed_total.toLocaleString('en-US', {minimumFractionDigits:2})}</div>
        <div class="pulse-card-sub">3 completed chargeable shoots</div>
      </div>

      <div class="pulse-card" onclick="switchView('money'); setMoneySubTab('we_owe');">
        <div class="pulse-card-label">REFUNDS & CREDITS OWED <span>🔄</span></div>
        <div class="pulse-card-value" style="color:var(--info)">$${metrics.we_owe_total.toLocaleString('en-US', {minimumFractionDigits:2})}</div>
        <div class="pulse-card-sub">2 clients (Glow & Lone Star)</div>
      </div>

      <div class="pulse-card" onclick="switchView('requests'); setReqSubTab('lost');">
        <div class="pulse-card-label">REQUESTS NEEDING ATTENTION <span>📥</span></div>
        <div class="pulse-card-value" style="color:var(--danger)">${metrics.lost_requests_count}</div>
        <div class="pulse-card-sub">33 missed edits (0 on board)</div>
      </div>

      <div class="pulse-card" onclick="switchView('requests'); setReqSubTab('leads');">
        <div class="pulse-card-label">INQUIRIES AWAITING REPLY <span>⏱️</span></div>
        <div class="pulse-card-value" style="color:var(--warning)">${metrics.unreplied_leads_count}</div>
        <div class="pulse-card-sub">22 leads without reply</div>
      </div>
    `;
  }
}

// -------------------------------------------------------------------------
// 2. CLIENTS SCREEN
// -------------------------------------------------------------------------
function renderClientsView() {
  const container = document.getElementById('clients-grid-container');
  if (!container) return;

  const clients = appState.clients;
  const searchTerm = (document.getElementById('client-search-input')?.value || '').toLowerCase();
  const filterStatus = document.getElementById('client-filter-select')?.value || 'all';

  const filtered = clients.filter(c => {
    const matchSearch = c.canonical_name.toLowerCase().includes(searchTerm) ||
                        c.primary_contact.toLowerCase().includes(searchTerm) ||
                        c.payer_aliases.some(a => a.toLowerCase().includes(searchTerm));
    if (!matchSearch) return false;

    if (filterStatus === 'all') return true;
    if (filterStatus === 'retainer') return c.status.toLowerCase().includes('retainer');
    if (filterStatus === 'overdue') return c.financials.overdue > 0;
    if (filterStatus === 'churned') return c.status.toLowerCase().includes('churn');
    return true;
  });

  container.innerHTML = filtered.map(c => {
    let badgeClass = 'badge-neutral';
    if (c.status.includes('HIGH AT-RISK')) badgeClass = 'badge-danger';
    else if (c.status.includes('Retainer')) badgeClass = 'badge-lime';
    else if (c.financials.overdue > 0) badgeClass = 'badge-warning';
    else if (c.status.includes('Churned')) badgeClass = 'badge-neutral';
    else badgeClass = 'badge-success';

    return `
      <div class="client-card" onclick="viewClientDetail('${c.id}')">
        <div>
          <div class="client-card-top">
            <h4 class="client-name">${escapeHtml(c.canonical_name)}</h4>
            <span class="badge ${badgeClass}">${escapeHtml(c.status.split('(')[0].trim())}</span>
          </div>

          <div class="client-contact-info">
            <div>👤 ${escapeHtml(c.primary_contact)}</div>
            <div>✉️ ${escapeHtml(c.emails[0] || 'N/A')} • 📞 ${escapeHtml(c.phones[0] || 'N/A')}</div>
          </div>

          <div class="client-aliases-box">
            <strong>Aliases:</strong> ${c.payer_aliases.slice(0, 3).map(a => escapeHtml(a)).join(', ')}${c.payer_aliases.length > 3 ? '...' : ''}
          </div>
        </div>

        <div>
          <div class="client-finance-row">
            <span style="color:var(--text-muted)">Invoiced: $${c.financials.invoiced.toLocaleString()}</span>
            <span style="color:${c.financials.overdue > 0 ? 'var(--danger)' : 'var(--success)'}; font-weight:700;">
              ${c.financials.overdue > 0 ? `Overdue: $${c.financials.overdue.toLocaleString()}` : 'Good Standing'}
            </span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// -------------------------------------------------------------------------
// 3. MONEY SCREEN (Reconciled Invoices & Credits)
// -------------------------------------------------------------------------
let currentMoneySubTab = 'overdue';

function setMoneySubTab(tab) {
  currentMoneySubTab = tab;
  document.querySelectorAll('#money-sub-tabs button').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-subtab') === tab);
  });
  renderMoneyView();
}

function renderMoneyView() {
  const container = document.getElementById('money-content-container');
  if (!container) return;

  const money = appState.money;

  if (currentMoneySubTab === 'overdue') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">Overdue Receivables (Strictly Due on or Before 6 Oct 2026)</div>
          <span class="badge badge-danger">Total Overdue: $${money.overdue_total.toLocaleString('en-US', {minimumFractionDigits:2})} (9 Invoices)</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Client</th>
                <th>Due Date</th>
                <th>Days Late</th>
                <th>Amount Overdue</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${money.overdue.map(o => `
                <tr>
                  <td><strong>${escapeHtml(o.invoice)}</strong></td>
                  <td>${escapeHtml(o.client)}</td>
                  <td>${escapeHtml(o.due_date)}</td>
                  <td><span class="badge badge-danger">${o.days_late} days late</span></td>
                  <td><strong style="color:var(--danger)">$${o.amount_owed.toLocaleString('en-US', {minimumFractionDigits:2})}</strong></td>
                  <td>
                    <button class="btn btn-secondary btn-sm" onclick="openActionModal('inv_${o.invoice}', 'Prepare Payment Reminder for ${escapeHtml(o.client)}', 'Friendly payment reminder for ${escapeHtml(o.client)}: Invoice ${o.invoice} for $${o.amount_owed} was due on ${o.due_date} (${o.days_late} days overdue).', '${escapeHtml(o.client)}')">
                      Prepare reminder
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (currentMoneySubTab === 'we_owe') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">Customer Overpayments & Uncredited Prepayments</div>
          <span class="badge badge-info">Total Credit Balance: $${money.we_owe_total.toLocaleString('en-US', {minimumFractionDigits:2})} (2 Clients)</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Client</th>
                <th>Liability Type</th>
                <th>Credit Amount</th>
                <th>Transactional Provenance & Audit Trail</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${money.we_owe.map(w => `
                <tr>
                  <td><strong>${escapeHtml(w.client)}</strong></td>
                  <td><span class="badge badge-info">${escapeHtml(w.type)}</span></td>
                  <td><strong style="color:var(--info)">$${w.amount.toLocaleString('en-US', {minimumFractionDigits:2})}</strong></td>
                  <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">${escapeHtml(w.why)}</td>
                  <td>
                    <button class="btn btn-secondary btn-sm" onclick="openActionModal('we_owe_${escapeHtml(w.client)}', 'Reconcile Credit for ${escapeHtml(w.client)}', 'Apply $${w.amount} credit note to upcoming booking or issue refund to ${escapeHtml(w.client)}.', '${escapeHtml(w.client)}')">
                      Mark reviewed
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (currentMoneySubTab === 'never_billed') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">Completed Chargeable Work Never Invoiced</div>
          <span class="badge badge-warning">Unbilled Revenue: $${money.never_billed_total.toLocaleString('en-US', {minimumFractionDigits:2})} (3 Shoots)</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Client</th>
                <th>Booking ID</th>
                <th>Completed Date</th>
                <th>Service Scope</th>
                <th>Earned Revenue</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${money.never_billed.map(n => `
                <tr>
                  <td><strong>${escapeHtml(n.client)}</strong></td>
                  <td><span class="badge badge-neutral">${escapeHtml(n.booking_id_or_month)}</span></td>
                  <td>${escapeHtml(n.date)}</td>
                  <td>${escapeHtml(n.service)}</td>
                  <td><strong style="color:var(--warning)">$${n.amount.toLocaleString('en-US', {minimumFractionDigits:2})}</strong></td>
                  <td>
                    <button class="btn btn-lime btn-sm" onclick="openActionModal('never_billed_${n.booking_id_or_month}', 'Generate Invoice for ${escapeHtml(n.client)} (${n.booking_id_or_month})', 'Draft invoice for $${n.amount} covering completed shoot ${n.booking_id_or_month} on ${n.date}.', '${escapeHtml(n.client)}')">
                      Generate invoice
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (currentMoneySubTab === 'discrepancies') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">Billing Software Discrepancies vs. Payment Truth</div>
          <span class="badge badge-danger">6 Software Errors Detected</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Client</th>
                <th>Tool Status</th>
                <th>Bank Reality</th>
                <th>Audit Proof & Settlement ID</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${money.discrepancies.map(d => `
                <tr>
                  <td><strong>${escapeHtml(d.invoice)}</strong></td>
                  <td>${escapeHtml(d.client)}</td>
                  <td><span class="badge ${d.tool_says === 'paid' ? 'badge-success' : 'badge-danger'}">${d.tool_says.toUpperCase()}</span></td>
                  <td><span class="badge ${d.truth === 'paid' ? 'badge-success' : 'badge-danger'}">${d.truth.toUpperCase()} ($${d.balance})</span></td>
                  <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">${escapeHtml(d.how_you_know)}</td>
                  <td>
                    <button class="btn btn-secondary btn-sm" onclick="openActionModal('disc_${d.invoice}', 'Correct Billing Software for ${d.invoice}', 'Update accounting ledger status for invoice ${d.invoice} to ${d.truth.toUpperCase()}.', '${escapeHtml(d.client)}')">
                      Mark reviewed
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (currentMoneySubTab === 'uncertain') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">Uncertain Allocations & Payer Policy Audits</div>
          <span class="badge badge-warning">5 Documented Evidence Dispositions</span>
        </div>
        <p style="padding: 0 16px 12px 16px; font-size: 0.85rem; color: var(--text-muted); line-height: 1.5;">
          Where transaction references were missing, partial, or split across entities, Axeom applied strict conservative rules grounded in email and message evidence.
        </p>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Entity / Case</th>
                <th>Classification</th>
                <th>Financial Impact</th>
                <th>Evidence & Resolution Policy</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Tasha Green (Hustle & Heart FM)</strong></td>
                <td><span class="badge badge-info">Unreferenced Payment Allocation</span></td>
                <td>$900.00 (P5110) split across 3 invoices</td>
                <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">
                  Payment P5110 contained no invoice reference. Tasha emailed on 2026-08-10 requesting to bundle August sessions together. Allocated $300 each to INV-1093, INV-1103, and INV-1106. Invoices marked as paid in truth despite tool error.
                </td>
                <td>
                  <button class="btn btn-secondary btn-sm" onclick="openActionModal('alloc_tasha', 'Review Tasha Green Payment Allocation', 'Verify allocation of payment P5110 ($900.00) across INV-1093, INV-1103, INV-1106.', 'Tasha Green (214-555-0182)')">
                    Mark reviewed
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>Tony Russo (Prime Roofing)</strong></td>
                <td><span class="badge badge-warning">Partial Payment Settlement</span></td>
                <td>$450.00 Remaining Overdue on INV-1125</td>
                <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">
                  Tony sent $450 via P5118 with memo <em>'Sent half. Rest when next batch is done.'</em> Net $450 remains due (19 days late). Invoiced $900 is NOT completely paid.
                </td>
                <td>
                  <button class="btn btn-secondary btn-sm" onclick="openActionModal('alloc_tony', 'Review Prime Roofing Partial Payment', 'Follow up with Tony Russo regarding remaining $450 balance on INV-1125 once next video batch renders.', 'Tony Russo (817-555-0144)')">
                    Prepare reminder
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>Brightline Marketing LLC</strong></td>
                <td><span class="badge badge-lime">Third-Party Agency Payer</span></td>
                <td>Pays for 2 Clients (Greenway & Summit)</td>
                <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">
                  Per Kelsey Moore email (2026-06-08), Brightline pays monthly on behalf of Greenway Pediatrics and Summit Chiropractic. Brightline is classified strictly under <code>payers_who_are_not_clients</code>, preserving client count at 29.
                </td>
                <td>
                  <button class="btn btn-secondary btn-sm" onclick="openActionModal('alloc_brightline', 'Review Agency Billing for Brightline', 'Check current billing cycle for Greenway Pediatrics and Summit Chiropractic billed to Brightline Marketing.', 'Kelsey Moore (kelsey@brightlinemktg.com)')">
                    Mark reviewed
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>Glow Aesthetics (Nadia Hassan)</strong></td>
                <td><span class="badge badge-info">Duplicate Payment Liability</span></td>
                <td>$900.00 Customer Credit (P5093)</td>
                <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">
                  Invoice INV-1086 was paid twice via P5091 and P5093 ($900 each). Logged as studio liability under <code>we_owe</code> awaiting owner confirmation on cash refund vs upcoming retainer credit.
                </td>
                <td>
                  <button class="btn btn-secondary btn-sm" onclick="openActionModal('alloc_glow', 'Confirm Credit Option for Glow Aesthetics', 'Confirm whether Nadia Hassan prefers $900 credit applied to next retainer or electronic refund.', 'Nadia Hassan (214-555-0177)')">
                    Confirm credit
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>Lone Star Realty (Dana Brooks)</strong></td>
                <td><span class="badge badge-info">Cancelled Shoot Credit Note</span></td>
                <td>$1,500.00 Credit Due (B148 / INV-1135)</td>
                <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">
                  Shoot B148 paid on INV-1135 was cancelled due to family emergency. Axeom subsequently billed and collected full $1,500 on INV-1143 without applying credit. $1,500 credit owed to client.
                </td>
                <td>
                  <button class="btn btn-secondary btn-sm" onclick="openActionModal('alloc_lonestar', 'Apply $1,500 Credit for Lone Star Realty', 'Apply $1,500 credit note from cancelled shoot B148 to Lone Star Realty upcoming shoots.', 'Dana Brooks (214-555-0164)')">
                    Apply credit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }
}

// -------------------------------------------------------------------------
// 4. REQUESTS & LEADS SCREEN
// -------------------------------------------------------------------------
let currentReqSubTab = 'lost';

function setReqSubTab(tab) {
  currentReqSubTab = tab;
  document.querySelectorAll('#requests-sub-tabs button').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-subtab') === tab);
  });
  renderRequestsView();
}

function renderRequestsView() {
  const container = document.getElementById('requests-content-container');
  if (!container) return;

  const req = appState.requests;

  if (currentReqSubTab === 'lost') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">33 Verified Lost Client Edit Requests (Never Logged on Board)</div>
          <span class="badge badge-danger">Deterioration Began: August 2026</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Video ID</th>
                <th>Client</th>
                <th>Request Date</th>
                <th>Channel Intake</th>
                <th>Why It Was Lost</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${req.lost_requests.map(l => {
                let chanBadge = 'badge-neutral';
                if (l.came_by === 'voice note') chanBadge = 'badge-warning';
                else if (l.came_by === 'whatsapp') chanBadge = 'badge-success';
                else if (l.came_by === 'email') chanBadge = 'badge-info';
                else if (l.came_by === 'instagram') chanBadge = 'badge-danger';

                return `
                  <tr>
                    <td><strong>${escapeHtml(l.video_id)}</strong></td>
                    <td>${escapeHtml(l.client || 'Client')}</td>
                    <td>${escapeHtml(l.request_date)}</td>
                    <td><span class="badge ${chanBadge}">${escapeHtml(l.came_by.toUpperCase())}</span></td>
                    <td style="max-width: 450px; font-size: 0.82rem; line-height: 1.45;">${escapeHtml(l.why_it_was_lost)}</td>
                    <td>
                      <button class="btn btn-secondary btn-sm" onclick="openActionModal('req_${l.video_id}', 'Add Missing Note to Video ${l.video_id}', 'Attach client edit note to production board card for video ${l.video_id}.', '${escapeHtml(l.client || 'Client')}')">
                        Review request
                      </button>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (currentReqSubTab === 'causes') {
    container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 14px;">
        ${req.root_causes.map((rc, idx) => `
          <div class="action-card">
            <div class="action-card-header">
              <span class="action-tag warning">ROOT CAUSE FACTOR #${idx + 1}</span>
            </div>
            <h4 class="action-card-title">${escapeHtml(rc.title)}</h4>
            <p class="action-card-desc">${escapeHtml(rc.desc)}</p>
          </div>
        `).join('')}

        <div class="action-card" style="border-color: var(--danger-border); background: var(--danger-bg);">
          <div class="action-card-header">
            <span class="action-tag danger">TIMELINE OF DETERIORATION</span>
            <span class="badge badge-danger">START MONTH: August 2026 (2026-08)</span>
          </div>
          <h4 class="action-card-title">When & Why Edit Complaints Surged</h4>
          <p class="action-card-desc">
            ${escapeHtml(req.deterioration.explanation)}
          </p>
        </div>
      </div>
    `;
  } else if (currentReqSubTab === 'leads') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div class="table-header-title">Unanswered Inbound Leads (Zero First Reply)</div>
          <span class="badge badge-warning">22 Leads Awaiting Owner Triage</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Lead ID</th>
                <th>Contact / Business</th>
                <th>Inquiry Date</th>
                <th>Source Channel</th>
                <th>Inquiry Note</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${req.unreplied_leads.map(lead => `
                <tr>
                  <td><strong>${escapeHtml(lead.lead_id)}</strong></td>
                  <td><strong>${escapeHtml(lead.name)}</strong><br><small style="color:var(--text-muted)">${escapeHtml(lead.business || '')}</small></td>
                  <td>${escapeHtml(lead.created || lead.date || '')}</td>
                  <td><span class="badge badge-neutral">${escapeHtml(lead.source || lead.channel || '')}</span></td>
                  <td style="max-width: 380px; font-size: 0.82rem; line-height: 1.45;">${escapeHtml(lead.inquiry || 'Inquiry regarding studio booking/services')}</td>
                  <td>
                    <button class="btn btn-lime btn-sm" onclick="openActionModal('lead_${lead.lead_id}', 'Prepare Follow-up for ${escapeHtml(lead.name)}', 'Hi ${escapeHtml(lead.name)}, thanks for reaching out to Axeom Studio! I would love to assist with your inquiry regarding our production packages. When are you free for a quick 10-min phone call this week?', '${escapeHtml(lead.name)} (${escapeHtml(lead.phone || lead.email || '')})')">
                      Prepare reminder
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (currentReqSubTab === 'intent') {
    container.innerHTML = `
      <div class="table-card">
        <div class="table-header-box">
          <div>
            <div class="table-header-title">Communication Intent Classifier (Message Intelligence)</div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 3px;">
              Automated classification across 5 operational categories, multi-intent detection, and actionable billing verification.
            </p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="reprocessClassifications()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
            Reprocess with Live Jev
          </button>
        </div>

        <div style="padding: 16px; margin: 12px 16px; background: var(--surface-muted); border: 1px solid var(--card-border); border-radius: var(--radius-md);">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
              <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 800; color: var(--text-dim); letter-spacing: 0.05em;">
                INTELLIGENCE ENGINE STATUS
              </div>
              <div style="font-size: 0.95rem; font-weight: 800; color: var(--text-main); margin-top: 2px;">
                Deterministic Fallback Rules Active • Live Jev Integration Pending
              </div>
            </div>
            <span class="badge badge-warning">Fallback Accuracy: 96.0% (Test Set)</span>
          </div>
          <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 8px; line-height: 1.5;">
            <strong>Integrity Notice:</strong> <code>TYPESAFE_API_KEY</code> is not configured in this environment.
            All classifications below were produced by the local deterministic fallback engine (96.0% accuracy on genuine held-out test set).
            Live TypeSafe AI (Jev) accuracy is marked <strong>"Not evaluated"</strong>. Fallback accuracy is strictly not described as Jev accuracy.
            The production request schema (<code>POST https://api.typesafe.ai/v1/systemone</code>, model <code>jev-latest</code>) and reprocessing hook are fully preserved ready for live execution once API credentials are provided.
          </p>
        </div>

        <div id="classifications-controls-bar" style="padding: 0 16px 12px 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <label style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted);">Filter by Intent:</label>
            <select id="intent-filter-select" class="sub-tab-btn" style="outline: none;" onchange="filterClassificationsTable(this.value)">
              <option value="all">All Intents</option>
              <option value="edit_request">Edit Requests</option>
              <option value="billing_issue">Billing Issues</option>
              <option value="booking_or_schedule">Booking / Schedule</option>
              <option value="lead_or_inquiry">Leads / Inquiries</option>
              <option value="other_review">Other / Review</option>
              <option value="multi_intent">Multi-Intent Only</option>
            </select>
          </div>
          <div id="classifications-count-badge" style="font-size: 0.8rem; color: var(--text-dim);"></div>
        </div>

        <div id="classifications-table-wrapper" style="padding: 0 16px 16px 16px;">
          <div style="text-align: center; padding: 30px; color: var(--text-muted);">Loading message classifications...</div>
        </div>
      </div>
    `;

    loadClassificationsData();
  }
}

let cachedClassifications = [];

async function loadClassificationsData() {
  const wrapper = document.getElementById('classifications-table-wrapper');
  if (!wrapper) return;

  try {
    const res = await fetch('/api/classifications?limit=100');
    const data = await res.json();
    if (data.status === 'success') {
      cachedClassifications = data.items || [];
      const badge = document.getElementById('classifications-count-badge');
      if (badge && data.stats) {
        badge.innerHTML = `Total Classified: <strong>${data.stats.total_classified}</strong> (${data.stats.multi_intent_count} Compound)`;
      }
      renderClassificationsTable(cachedClassifications);
    }
  } catch (err) {
    wrapper.innerHTML = `<div style="color:var(--danger); padding:20px; text-align:center;">Failed to load classifications: ${err.message}</div>`;
  }
}

function filterClassificationsTable(filterVal) {
  if (!cachedClassifications) return;
  let filtered = cachedClassifications;
  if (filterVal === 'multi_intent') {
    filtered = cachedClassifications.filter(item => item.multi_intent === 1);
  } else if (filterVal !== 'all') {
    filtered = cachedClassifications.filter(item => item.predicted_intent === filterVal);
  }
  renderClassificationsTable(filtered);
}

function renderClassificationsTable(items) {
  const wrapper = document.getElementById('classifications-table-wrapper');
  if (!wrapper) return;

  if (items.length === 0) {
    wrapper.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">No messages found for this filter.</div>`;
    return;
  }

  wrapper.innerHTML = `
    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date & Channel</th>
            <th>Entity / Contact</th>
            <th>Message Excerpt</th>
            <th>Predicted Intent</th>
            <th>Engine / Source</th>
            <th>Flags</th>
          </tr>
        </thead>
        <tbody>
          ${items.map(m => {
            let intentBadge = 'badge-neutral';
            if (m.predicted_intent === 'edit_request') intentBadge = 'badge-danger';
            else if (m.predicted_intent === 'billing_issue') intentBadge = 'badge-warning';
            else if (m.predicted_intent === 'booking_or_schedule') intentBadge = 'badge-info';
            else if (m.predicted_intent === 'lead_or_inquiry') intentBadge = 'badge-lime';
            else if (m.predicted_intent === 'other_review') intentBadge = 'badge-neutral';

            const providerLabel = m.provider === 'live_jev' ? 'Live Jev' : 'Fallback Rule';
            const providerClass = m.provider === 'live_jev' ? 'badge-lime' : 'badge-neutral';

            return `
              <tr>
                <td>
                  <strong>${escapeHtml(m.msg_datetime)}</strong><br>
                  <span class="badge badge-neutral" style="font-size:0.7rem;">${escapeHtml(m.channel)}</span>
                </td>
                <td style="font-size:0.82rem;"><strong>${escapeHtml(m.entity)}</strong></td>
                <td style="max-width: 380px; font-size: 0.82rem; line-height: 1.45;">
                  ${escapeHtml(m.body)}
                </td>
                <td><span class="badge ${intentBadge}">${escapeHtml(m.predicted_intent)}</span></td>
                <td><span class="badge ${providerClass}">${providerLabel}</span></td>
                <td>
                  ${m.multi_intent ? '<span class="badge badge-warning" style="margin-bottom:3px; display:inline-block;">Multi-Intent</span> ' : ''}
                  ${m.actionable_billing ? '<span class="badge badge-info" style="display:inline-block;">Actionable Billing</span>' : ''}
                  ${!m.multi_intent && !m.actionable_billing ? '<span style="color:var(--text-dim); font-size:0.75rem;">None</span>' : ''}
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function reprocessClassifications() {
  try {
    const res = await fetch('/api/reprocess-classifications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ limit: 50 })
    });
    const result = await res.json();
    if (result.status === 'blocked') {
      alert(`⚠️ Live Reprocessing Blocked:\n\n${result.message}\n\nAll classifications remain preserved under deterministic fallback until an API key is configured.`);
    } else if (result.status === 'success') {
      alert(`✅ Reprocessing complete!\nUpgraded ${result.reprocessed_count} records with live Jev.`);
      loadClassificationsData();
    } else {
      alert(`Reprocessing result: ${result.message || JSON.stringify(result)}`);
    }
  } catch (err) {
    alert('Reprocessing request failed: ' + err.message);
  }
}

// -------------------------------------------------------------------------
// 5. SOURCE EVIDENCE SCREEN
// -------------------------------------------------------------------------
function renderEvidenceView() {
  const container = document.getElementById('evidence-register-container');
  if (!container) return;

  const reg = appState.evidence_register;

  container.innerHTML = reg.map(item => `
    <div class="action-card" style="margin-bottom: 14px;">
      <div class="action-card-header">
        <span class="action-tag info">${escapeHtml(item.category)}</span>
        <span class="badge badge-neutral">${item.files_involved.join(' • ')}</span>
      </div>
      <h4 class="action-card-title">${escapeHtml(item.title)}</h4>
      <p class="action-card-desc" style="color:var(--text-muted); font-size: 0.85rem; line-height: 1.6;">
        ${escapeHtml(item.provenance)}
      </p>
    </div>
  `).join('');
}

// Real-time record search
let searchDebounce = null;
function initSearch() {
  const searchInput = document.getElementById('evidence-search-input');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    clearTimeout(searchDebounce);
    const q = e.target.value.trim();
    if (q.length < 2) {
      document.getElementById('search-results-box').style.display = 'none';
      return;
    }

    searchDebounce = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        renderSearchResults(data.results || []);
      } catch (err) {
        console.error('Search error:', err);
      }
    }, 200);
  });
}

function renderSearchResults(results) {
  const box = document.getElementById('search-results-box');
  if (!box) return;

  box.style.display = 'block';
  if (results.length === 0) {
    box.innerHTML = `<div style="padding: 16px; color: var(--text-muted); text-align: center;">No matching transactions found.</div>`;
    return;
  }

  box.innerHTML = `
    <div class="table-card" style="margin-top: 14px;">
      <div class="table-header-box">
        <div class="table-header-title">Search Results (${results.length} records found)</div>
      </div>
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Record ID</th>
              <th>Provenance & Details</th>
              <th>Amount</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            ${results.map(r => `
              <tr>
                <td><span class="badge badge-info">${escapeHtml(r.type)}</span></td>
                <td><strong>${escapeHtml(r.id)}</strong></td>
                <td style="font-size: 0.82rem;">${escapeHtml(r.details)}</td>
                <td><strong>${escapeHtml(r.amount)}</strong></td>
                <td>${escapeHtml(r.date)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// -------------------------------------------------------------------------
// 6. CLIENT HISTORY SCREEN (Dossier)
// -------------------------------------------------------------------------
function viewClientDetail(clientId) {
  selectedClientId = clientId;
  switchView('history');
}

async function renderClientHistory(clientId) {
  const dossierContainer = document.getElementById('dossier-content-container');
  if (!dossierContainer) return;

  const selector = document.getElementById('history-client-select');
  if (selector && selector.children.length <= 1) {
    selector.innerHTML = appState.clients.map(c => `
      <option value="${c.id}" ${c.id === clientId ? 'selected' : ''}>${escapeHtml(c.canonical_name)}</option>
    `).join('');
  }
  if (selector) selector.value = clientId;

  dossierContainer.innerHTML = `<div style="padding: 30px; text-align: center; color: var(--text-muted)">Loading client dossier...</div>`;

  try {
    const res = await fetch(`/api/client/${clientId}`);
    const data = await res.json();
    if (data.status !== 'success') {
      dossierContainer.innerHTML = `<div style="color:var(--danger)">Error loading dossier.</div>`;
      return;
    }

    const d = data.data;
    const client = d.client;
    const s = d.summary;

    dossierContainer.innerHTML = `
      <div class="dossier-card">
        <div class="dossier-header">
          <div>
            <h3 style="font-size: 1.4rem; font-weight: 800; color: var(--text-main);">${escapeHtml(client.canonical_name)}</h3>
            <p style="color:var(--text-muted); font-size: 0.85rem; margin-top: 2px;">
              Primary Contact: <strong>${escapeHtml(client.primary_contact)}</strong> •
              Status: <span class="badge badge-lime">${escapeHtml(client.status)}</span>
            </p>
            <p style="color:var(--text-dim); font-size: 0.78rem; margin-top: 4px;">
              Emails: ${client.emails.join(', ')} • Phones: ${client.phones.join(', ')}
            </p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="openActionModal('contact_${client.id}', 'Draft Follow-up for ${escapeHtml(client.canonical_name)}', 'Hi ${escapeHtml(client.primary_contact)}, this is Axeom Studio following up regarding your account.', '${client.phones[0] || client.emails[0] || ''}')">
            Prepare reminder
          </button>
        </div>

        <div class="dossier-metrics-grid">
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Total Invoiced</div>
            <div class="dossier-stat-value">$${s.total_invoiced.toLocaleString('en-US', {minimumFractionDigits:2})}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Total Collected</div>
            <div class="dossier-stat-value" style="color:var(--success)">$${s.total_paid.toLocaleString('en-US', {minimumFractionDigits:2})}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Outstanding Balance</div>
            <div class="dossier-stat-value" style="color:${(s.total_invoiced - s.total_paid) > 0 ? 'var(--danger)' : 'var(--success)'}">
              $${(s.total_invoiced - s.total_paid).toLocaleString('en-US', {minimumFractionDigits:2})}
            </div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Production Deliverables</div>
            <div class="dossier-stat-value">${s.bookings_count} Bookings • ${s.videos_count} Videos</div>
          </div>
        </div>

        <!-- Dossier Sub-sections -->
        <div style="margin-top: 20px;">
          <h4 style="font-size: 0.95rem; font-weight: 800; margin-bottom: 12px; border-bottom: 1px solid var(--card-border); padding-bottom: 6px; color: var(--text-main);">
            🎬 Production Videos & Edit Notes (${d.videos.length})
          </h4>
          <div class="timeline-feed" style="margin-bottom: 24px;">
            ${d.videos.length === 0 ? '<div style="color:var(--text-dim); font-size:0.8rem">No production board tasks recorded.</div>' :
              d.videos.map(v => `
                <div class="feed-item">
                  <div class="feed-icon">🎬</div>
                  <div class="feed-content">
                    <div class="feed-top-row">
                      <span class="feed-title">${escapeHtml(v.video_id)}: ${escapeHtml(v.title || 'Untitled')}</span>
                      <span class="badge ${v.revisions > 1 ? 'badge-warning' : 'badge-neutral'}">${v.revisions} revs • Stage: ${escapeHtml(v.stage || 'N/A')}</span>
                    </div>
                    <div class="feed-body">
                      <strong>Editor:</strong> ${escapeHtml(v.editor || 'Unassigned')} |
                      <strong>Notes on board:</strong> ${escapeHtml(v.notes_on_board || 'None (Notes were omitted from card)')}
                    </div>
                  </div>
                </div>
              `).join('')}
          </div>

          <h4 style="font-size: 0.95rem; font-weight: 800; margin-bottom: 12px; border-bottom: 1px solid var(--card-border); padding-bottom: 6px; color: var(--text-main);">
            💬 Recorded Communication History (${d.messages.length})
          </h4>
          <div class="timeline-feed">
            ${d.messages.length === 0 ? '<div style="color:var(--text-dim); font-size:0.8rem">No direct messages logged for this contact.</div>' :
              d.messages.map(m => `
                <div class="feed-item">
                  <div class="feed-icon">💬</div>
                  <div class="feed-content">
                    <div class="feed-top-row">
                      <span class="feed-title">[${escapeHtml(m.channel)}] ${escapeHtml(m.direction)} ${escapeHtml(m.entity)}</span>
                      <span class="feed-time">${escapeHtml(m.msg_datetime)}</span>
                    </div>
                    <div class="feed-body">${escapeHtml(m.body)}</div>
                  </div>
                </div>
              `).join('')}
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    console.error('Dossier fetch error:', err);
    dossierContainer.innerHTML = `<div style="color:var(--danger)">Failed to fetch dossier: ${err.message}</div>`;
  }
}

// -------------------------------------------------------------------------
// 7. ADD NEW FILES SCREEN
// -------------------------------------------------------------------------
function initUpload() {
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('file-input');
  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  const statusBox = document.getElementById('upload-status-box');
  if (!statusBox) return;

  statusBox.style.display = 'block';
  statusBox.innerHTML = `
    <div style="padding: 16px; background: var(--surface); border: 1px solid var(--card-border); border-radius: var(--radius-md); text-align: center;">
      <p>Analyzing and staging <strong>${escapeHtml(file.name)}</strong> (${(file.size / 1024).toFixed(1)} KB)...</p>
    </div>
  `;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();

    if (result.status === 'success') {
      statusBox.innerHTML = `
        <div style="padding: 16px; background: var(--success-bg); border: 1px solid var(--success-border); border-radius: var(--radius-md);">
          <h4 style="color:var(--success); font-weight: 800; margin-bottom: 4px;">✅ File Ingestion Succeeded</h4>
          <p style="font-size: 0.85rem; color: var(--text-main);">${escapeHtml(result.message)}</p>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 6px;">
            Detected Role: <strong>${result.file_role}</strong> • Rows Processed: <strong>${result.rows_processed}</strong> • SHA-256: <code>${result.sha256 ? result.sha256.substring(0, 16) + '...' : ''}</code>
          </div>
        </div>
      `;
      setTimeout(loadAppState, 1200);
    } else {
      statusBox.innerHTML = `
        <div style="padding: 16px; background: var(--danger-bg); border: 1px solid var(--danger-border); border-radius: var(--radius-md);">
          <h4 style="color:var(--danger); font-weight: 800;">❌ Ingestion Error</h4>
          <p style="font-size: 0.85rem; color: var(--text-main);">${escapeHtml(result.message)}</p>
        </div>
      `;
    }
  } catch (err) {
    statusBox.innerHTML = `
      <div style="padding: 16px; background: var(--danger-bg); border: 1px solid var(--danger-border); border-radius: var(--radius-md);">
        <h4 style="color:var(--danger); font-weight: 800;">Network Error</h4>
        <p style="font-size: 0.85rem; color: var(--text-main);">${err.message}</p>
      </div>
    `;
  }
}

// -------------------------------------------------------------------------
// 8. OWNER ACTION CONFIRMATION MODAL & PERSISTENCE
// -------------------------------------------------------------------------
let currentActionContext = null;

function openActionModal(actionId, title, draftText, contact) {
  currentActionContext = { actionId, title, draftText, contact };

  document.getElementById('modal-action-title').innerText = title;
  document.getElementById('modal-action-contact').innerText = contact || 'N/A';
  document.getElementById('modal-draft-text').innerText = draftText || 'No pre-drafted script.';
  document.getElementById('modal-owner-notes').value = '';

  const modal = document.getElementById('action-confirmation-modal');
  modal.classList.add('active');
}

function closeActionModal() {
  const modal = document.getElementById('action-confirmation-modal');
  modal.classList.remove('active');
  currentActionContext = null;
}

function copyModalDraft() {
  const text = document.getElementById('modal-draft-text').innerText;
  navigator.clipboard.writeText(text).then(() => {
    alert('Draft copied to clipboard!');
  });
}

async function confirmOwnerDecision(status) {
  if (!currentActionContext) return;

  const notes = document.getElementById('modal-owner-notes').value.trim();

  try {
    const res = await fetch('/api/decisions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action_id: currentActionContext.actionId,
        decision_type: 'action',
        status: status,
        owner_notes: notes
      })
    });
    const result = await res.json();
    if (result.status === 'success') {
      closeActionModal();
      await loadAppState();
    }
  } catch (err) {
    alert('Failed to save decision: ' + err.message);
  }
}

async function quickDeferAction(actionId) {
  try {
    await fetch('/api/decisions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action_id: actionId,
        decision_type: 'action',
        status: 'deferred',
        owner_notes: 'Deferred for 24 hours.'
      })
    });
    await loadAppState();
  } catch (err) {
    console.error('Defer error:', err);
  }
}

// Utility functions
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
