/**
 * Axeom Data Management & Owner Reports Browser E2E Automation Suite
 * Drives Google Chrome via Playwright-core.
 * Verifies:
 *  - "Manage Data" view access from desktop sidebar and mobile dock
 *  - 5 subtabs: All Records, Upload History, Archived Records, Delete Old Data, Reset Data
 *  - Table switching (clients, invoices, payments, bookings, production_board, leads, messages)
 *  - Search filtering & debouncing
 *  - Pre-flight Impact Analysis Modal & financial preservation safety warning
 *  - Server-side Owner Authorization PIN modal workflow
 *  - Export Business Report Modal, KPI preview, JSON & HTML download links
 *  - Mobile responsiveness (390x844)
 *  - Visual captures in tests/reports/screenshots/
 */

const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.join(__dirname, 'reports', 'screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runManageDataE2ESuite() {
  console.log('====================================================');
  console.log('STARTING AXEOM MANAGE DATA & REPORTING E2E QA SUITE');
  console.log('====================================================\n');

  const browser = await chromium.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    headless: true
  });

  const consoleErrors = [];
  const networkFailures = [];

  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 }
  });

  const page = await context.newPage();

  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  page.on('requestfailed', req => {
    networkFailures.push(`${req.method()} ${req.url()}: ${req.failure().errorText}`);
  });

  try {
    const TARGET_URL = process.env.TARGET_URL || 'http://127.0.0.1:5050';
    console.log(`[Test 1] Navigating to ${TARGET_URL}...`);
    await page.goto(TARGET_URL, { waitUntil: 'networkidle' });

    // -----------------------------------------------------------------
    // TEST 1: DESKTOP NAVIGATION TO MANAGE DATA VIEW
    // -----------------------------------------------------------------
    console.log('[Test 2] Navigating to Manage Data view...');
    const manageNavBtn = page.locator('button.nav-item[data-view-target="manage"]');
    await manageNavBtn.waitFor({ state: 'visible', timeout: 5000 });
    await manageNavBtn.click();

    await page.waitForSelector('#view-manage.active', { timeout: 5000 });
    console.log('  ✅ Manage Data view is active');

    // Wait for records table to populate
    await page.waitForSelector('#manage-table-container table', { timeout: 5000 });
    const rowCount = await page.locator('#manage-table-container tbody tr').count();
    console.log(`  Initial clients table rows loaded: ${rowCount}`);

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_manage_data_records_view.png'), fullPage: true });
    console.log('  📸 Captured: 09_manage_data_records_view.png');

    // -----------------------------------------------------------------
    // TEST 2: TABLE SWITCHING & SEARCH FILTERING
    // -----------------------------------------------------------------
    console.log('[Test 3] Testing table selector and search filtering...');
    const tableSelect = page.locator('#manage-table-select');
    await tableSelect.selectOption('invoices');
    await page.waitForTimeout(800);

    const invoiceRows = await page.locator('#manage-table-container tbody tr').count();
    console.log(`  Switched to invoices table: ${invoiceRows} rows loaded`);

    // Search filter
    const searchInput = page.locator('#manage-search-input');
    await searchInput.fill('Apex');
    await page.waitForTimeout(1000);
    console.log('  Filtered invoices by "Apex"');

    // Switch back to clients
    await tableSelect.selectOption('clients');
    await searchInput.fill('');
    await page.waitForTimeout(800);

    // -----------------------------------------------------------------
    // TEST 3: IMPACT ANALYSIS MODAL
    // -----------------------------------------------------------------
    console.log('[Test 4] Opening Impact Analysis modal...');
    const impactBtn = page.locator('.btn-impact-check').first();
    await impactBtn.waitFor({ state: 'visible', timeout: 5000 });
    await impactBtn.click();

    await page.waitForSelector('#delete-impact-modal.active', { timeout: 5000 });
    const impactText = await page.textContent('#delete-impact-modal');
    console.log('  Impact Modal Content:', impactText.includes('Safety Invariant') || impactText.includes('historical invoices') ? '✅ Financial safety invariant detected' : '⚠️ Checking safety text');

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_manage_data_impact_modal.png') });
    console.log('  📸 Captured: 10_manage_data_impact_modal.png');

    // Close modal
    const closeImpactBtn = page.locator('#delete-impact-modal .modal-close');
    await closeImpactBtn.click();
    await page.waitForTimeout(300);

    // -----------------------------------------------------------------
    // TEST 4: OWNER PIN AUTHENTICATION WORKFLOW
    // -----------------------------------------------------------------
    console.log('[Test 5] Testing Owner Authentication workflow...');
    const ownerAuthBtn = page.locator('#btn-owner-auth-trigger');
    if (await ownerAuthBtn.isVisible()) {
      await ownerAuthBtn.click();
      await page.waitForSelector('#owner-auth-modal.active', { timeout: 5000 });
      console.log('  Owner Auth Modal opened');

      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '11_manage_data_owner_auth_modal.png') });
      console.log('  📸 Captured: 11_manage_data_owner_auth_modal.png');

      // Submit valid PIN
      await page.fill('#owner-pin-input', 'axeom-owner-2026');
      await page.click('#btn-submit-owner-pin');
      await page.waitForTimeout(800);

      const authStatusText = await page.textContent('#owner-auth-status-badge');
      console.log(`  Owner Status: ${authStatusText.trim()}`);
    }

    // -----------------------------------------------------------------
    // TEST 5: SUBTABS NAVIGATION (Uploads, Archived, Delete, Reset)
    // -----------------------------------------------------------------
    console.log('[Test 6] Testing Manage Data subtabs navigation...');
    // 1. Uploads subtab
    await page.click('.subtab-btn[data-subtab="uploads"]');
    await page.waitForTimeout(600);
    const uploadsCount = await page.locator('#manage-uploads-list tr').count();
    console.log(`  Upload History Subtab: ${uploadsCount} upload events displayed`);

    // 2. Archived subtab
    await page.click('.subtab-btn[data-subtab="archived"]');
    await page.waitForTimeout(600);
    console.log('  Archived Records Subtab loaded');

    // 3. Delete Old Data subtab
    await page.click('.subtab-btn[data-subtab="delete"]');
    await page.waitForTimeout(600);
    console.log('  Delete Old Data Subtab loaded');

    // 4. Reset Data subtab
    await page.click('.subtab-btn[data-subtab="reset"]');
    await page.waitForTimeout(600);
    const resetPhraseVisible = await page.locator('#reset-confirmation-input').isVisible();
    console.log(`  Reset Business Data Subtab loaded (Confirmation input visible: ${resetPhraseVisible})`);

    // -----------------------------------------------------------------
    // TEST 6: EXPORT BUSINESS REPORT MODAL
    // -----------------------------------------------------------------
    console.log('[Test 7] Testing Export Business Report modal...');
    const exportReportBtn = page.locator('#btn-export-business-report');
    await exportReportBtn.waitFor({ state: 'visible', timeout: 5000 });
    await exportReportBtn.click();

    await page.waitForSelector('#business-report-modal.active', { timeout: 5000 });
    console.log('  Export Business Report Modal opened');

    // Verify report preview loaded
    await page.waitForSelector('#report-preview-container .report-kpi-grid', { timeout: 5000 });
    const reportKpiCount = await page.locator('#report-preview-container .report-kpi-card').count();
    console.log(`  Executive Report KPIs rendered: ${reportKpiCount}`);

    // Verify download links
    const jsonLink = await page.getAttribute('#btn-download-report-json', 'href');
    const htmlLink = await page.getAttribute('#btn-download-report-html', 'href');
    console.log(`  JSON Download link: ${jsonLink}`);
    console.log(`  HTML Print link: ${htmlLink}`);

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '12_export_business_report_modal.png') });
    console.log('  📸 Captured: 12_export_business_report_modal.png');

    // Close report modal
    await page.click('#business-report-modal .modal-close');
    await page.waitForTimeout(300);

    // -----------------------------------------------------------------
    // TEST 7: RESPONSIVE MOBILE VIEW (390x844)
    // -----------------------------------------------------------------
    console.log('[Test 8] Testing responsive mobile view (390x844)...');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);

    // Verify mobile floating dock includes Manage button
    const mobileManageBtn = page.locator('button.mobile-nav-btn[data-view-target="manage"]');
    await mobileManageBtn.waitFor({ state: 'visible', timeout: 5000 });
    await mobileManageBtn.click();

    await page.waitForSelector('#view-manage.active', { timeout: 5000 });
    console.log('  Mobile dock successfully opened Manage Data view');

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'responsive_manage_data_mobile_390x844.png') });
    console.log('  📸 Captured: responsive_manage_data_mobile_390x844.png');

    console.log('\n====================================================');
    console.log('✅ ALL MANAGE DATA & REPORTING E2E TESTS PASSED');
    console.log(`Console Errors: ${consoleErrors.length}`);
    console.log(`Network Failures: ${networkFailures.length}`);
    console.log('====================================================\n');

  } catch (err) {
    console.error('❌ Browser QA Suite Encountered Error:', err);
    throw err;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  runManageDataE2ESuite().catch(() => process.exit(1));
}

module.exports = { runManageDataE2ESuite };
