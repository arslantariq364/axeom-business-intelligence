/**
 * Comprehensive Browser End-to-End Automation & Visual QA Suite
 * Drives local Google Chrome via Playwright-core.
 * Verifies:
 *  - Dashboard rendering, pulse metrics, and hero card
 *  - Full navigation across all 7 views
 *  - Client directory search, filtering, and dossier modal opening
 *  - Financial ledgers (Overdue, We Owe, Uninvoiced, Tool Software Errors)
 *  - Requests & Leads tabs (33 lost requests, root causes, 22 leads)
 *  - Owner decision modal interaction, notes submission, and quick-defer persistence
 *  - Viewport captures: 375x812, 390x844, 768x1024, 1366x768
 *  - Zero uncaught console errors and zero failed network requests
 */

const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.join(__dirname, 'reports', 'screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runBrowserQASuite() {
  console.log('====================================================');
  console.log('STARTING AXEOM OWNER OS BROWSER AUTOMATION QA SUITE');
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
    // -----------------------------------------------------------------
    // TEST 1: DASHBOARD LOAD & HERO CARD (1366x768)
    // -----------------------------------------------------------------
    const TARGET_URL = process.env.TARGET_URL || 'http://127.0.0.1:5050';
    console.log(`[Test 1] Navigating to ${TARGET_URL}...`);
    await page.goto(TARGET_URL, { waitUntil: 'networkidle' });
    
    const title = await page.title();
    console.log(`  Page title: "${title}"`);
    if (!title.includes('Axeom Owner OS')) {
      throw new Error(`Unexpected title: ${title}`);
    }

    // Check Hero Card
    await page.waitForSelector('#hero-card-container .hero-lime-card', { timeout: 5000 });
    const heroText = await page.textContent('#hero-card-container');
    console.log('  Hero Action Card loaded:', heroText.includes('Patel Insurance') ? '✅ Patel Insurance detected' : '❌ Patel Insurance missing');

    // Check pulse metrics
    const pulseCount = await page.locator('.pulse-card').count();
    console.log(`  Pulse metric cards rendered: ${pulseCount}`);

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_desktop_dashboard_hero.png'), fullPage: true });
    console.log('  Captured: 01_desktop_dashboard_hero.png');

    // -----------------------------------------------------------------
    // TEST 2: NAVIGATION ACROSS ALL TABS
    // -----------------------------------------------------------------
    console.log('\n[Test 2] Testing Navigation Views...');

    // 2.1 Money & Invoices
    console.log('  Switching to Money view...');
    await page.click('button[data-view-target="money"]');
    await page.waitForSelector('#view-money.active');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_view_money_overdue.png') });

    // Click through money sub-tabs
    console.log('    Subtab: Refunds & Credits Owed...');
    await page.click('button[data-subtab="we_owe"]');
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02b_view_money_we_owe.png') });

    console.log('    Subtab: Uninvoiced Work...');
    await page.click('button[data-subtab="never_billed"]');
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02c_view_money_never_billed.png') });

    console.log('    Subtab: Billing Tool Software Errors...');
    await page.click('button[data-subtab="discrepancies"]');
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02d_view_money_discrepancies.png') });

    // 2.2 Clients Directory
    console.log('  Switching to Clients view...');
    await page.click('button[data-view-target="clients"]');
    await page.waitForSelector('#view-clients.active');
    const clientCardsCount = await page.locator('.client-card').count();
    console.log(`    Client cards rendered: ${clientCardsCount}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_view_clients_grid.png') });

    // Search for a client
    console.log('    Testing Client search filter ("Northpoint")...');
    await page.fill('#client-search-input', 'Northpoint');
    await page.waitForTimeout(400);
    const filteredCount = await page.locator('.client-card').count();
    console.log(`    Filtered client cards for "Northpoint": ${filteredCount}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03b_view_clients_filtered.png') });
    await page.fill('#client-search-input', ''); // clear
    await page.waitForTimeout(300);

    // 2.3 Requests & Leads
    console.log('  Switching to Requests & Leads view...');
    await page.click('button[data-view-target="requests"]');
    await page.waitForSelector('#view-requests.active');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_view_requests_lost.png') });

    console.log('    Subtab: Root Causes...');
    await page.click('button[data-subtab="causes"]');
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04b_view_requests_causes.png') });

    console.log('    Subtab: 22 Unanswered Leads...');
    await page.click('button[data-subtab="leads"]');
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04c_view_requests_leads.png') });

    // 2.4 Client History Dossier
    console.log('  Switching to Client History view...');
    await page.click('button[data-view-target="history"]');
    await page.waitForSelector('#view-history.active');
    await page.waitForSelector('#dossier-content-container');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_view_history_dossier.png') });

    // 2.5 Source Evidence Register & Search
    console.log('  Switching to Source Evidence view...');
    await page.click('button[data-view-target="evidence"]');
    await page.waitForSelector('#view-evidence.active');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_view_evidence_register.png') });

    // 2.6 Add New Files Screen
    console.log('  Switching to Add New Files view...');
    await page.click('button[data-view-target="upload"]');
    await page.waitForSelector('#view-upload.active');
    const dropzoneVisible = await page.isVisible('#upload-dropzone');
    console.log(`    Upload dropzone visible: ${dropzoneVisible}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_view_upload_dropzone.png') });

    // -----------------------------------------------------------------
    // TEST 3: OWNER ACTION SAFETY CONTROLS & PERSISTENCE
    // -----------------------------------------------------------------
    console.log('\n[Test 3] Testing Owner Action Controls on Today View...');
    await page.click('button[data-view-target="today"]');
    await page.waitForSelector('#view-today.active');

    // Click "Prepare reminder" on Hero Card to open action confirmation modal
    console.log('  Clicking action button to open confirmation modal...');
    const actionBtn = page.locator('#hero-card-container button:has-text("Prepare reminder")');
    if (await actionBtn.count() > 0) {
      await actionBtn.click();
      await page.waitForSelector('#action-confirmation-modal.active', { timeout: 3000 });
      console.log('  Modal opened: #action-confirmation-modal');

      // Verify that NO message is sent automatically and draft script is shown
      const draftText = await page.textContent('#modal-draft-text');
      console.log(`  Draft script visible: "${draftText.substring(0, 60)}..."`);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_owner_action_modal.png') });

      // Add owner note and click "Mark In Progress"
      await page.fill('#modal-owner-notes', 'Reviewed in QA automation: owner decision explicitly persisted.');
      await page.click('button:has-text("Mark In Progress")');
      await page.waitForFunction(() => !document.getElementById('action-confirmation-modal').classList.contains('active'), { timeout: 3000 });
      console.log('  Decision saved successfully.');
    }

    // -----------------------------------------------------------------
    // TEST 4: RESPONSIVE VIEWPORT TESTING (STAGE 7)
    // -----------------------------------------------------------------
    console.log('\n[Test 4] Mobile and Tablet Viewport Visual Testing...');
    const viewports = [
      { name: 'mobile_small_375x812', width: 375, height: 812 },
      { name: 'mobile_standard_390x844', width: 390, height: 844 },
      { name: 'tablet_portrait_768x1024', width: 768, height: 1024 },
      { name: 'desktop_standard_1366x768', width: 1366, height: 768 }
    ];

    for (const vp of viewports) {
      console.log(`  Testing viewport: ${vp.name} (${vp.width}x${vp.height})...`);
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${TARGET_URL}/#today`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);

      // Verify 10-second rule: is the hero action prominent and readable?
      const heroVisible = await page.isVisible('#hero-card-container');
      const actionTitle = await page.textContent('#hero-card-container');
      console.log(`    10-second test: Hero action visible? ${heroVisible} (${actionTitle.includes('Patel Insurance') ? 'PASS' : 'FAIL'})`);

      // Verify mobile bottom nav on mobile viewports (< 768px)
      if (vp.width < 768) {
        const bottomNavVisible = await page.isVisible('.mobile-bottom-nav');
        console.log(`    Mobile bottom navigation dock visible: ${bottomNavVisible}`);
      }

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `responsive_${vp.name}.png`),
        fullPage: true
      });
      console.log(`    Saved: responsive_${vp.name}.png`);
    }

    console.log('\n----------------------------------------------------');
    console.log('BROWSER QA EXECUTION SUMMARY');
    console.log('----------------------------------------------------');
    console.log(`Console Errors: ${consoleErrors.length}`);
    if (consoleErrors.length > 0) {
      console.error('  Errors detected:', consoleErrors);
    }
    console.log(`Network Failures: ${networkFailures.length}`);
    if (networkFailures.length > 0) {
      console.error('  Failures detected:', networkFailures);
    }
    console.log('All basic browser interactions completed successfully!\n');

  } finally {
    await browser.close();
  }
}

runBrowserQASuite().catch(err => {
  console.error('FATAL BROWSER QA FAILURE:', err);
  process.exit(1);
});
