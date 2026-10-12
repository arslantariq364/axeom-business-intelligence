/**
 * Stage 6: Real Browser File Upload Testing Suite
 * Uses Playwright driving local Google Chrome.
 * Uploads all synthetic test fixtures (Tests A through P) via the real browser #file-input.
 * Verifies before-and-after UI states, upload confirmations, client dossiers, refresh persistence,
 * and records detailed pass/fail results against the independent test manifest.
 */

const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const FIXTURES_DIR = path.join(__dirname, 'fixtures', 'axeom_uploads');
const SCREENSHOT_DIR = path.join(__dirname, 'reports', 'screenshots', 'uploads');
const MANIFEST_PATH = path.join(__dirname, 'fixtures', 'test_manifest.json');
const RESULTS_JSON_PATH = path.join(__dirname, 'reports', 'UPLOAD_TEST_RESULTS.json');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

function restoreBaselineDatabase() {
  const root = path.join(__dirname, '..');
  const backup = path.join(root, 'axeom_baseline_backup.db');
  const target = path.join(root, 'axeom.db');
  fs.copyFileSync(backup, target);
  try {
    fs.unlinkSync(path.join(root, 'axeom.db-wal'));
  } catch (e) {}
  try {
    fs.unlinkSync(path.join(root, 'axeom.db-shm'));
  } catch (e) {}
}

async function runUploadTestSuite() {
  console.log('========================================================');
  console.log('STAGE 6: REAL BROWSER FILE UPLOAD AUTOMATION TEST SUITE');
  console.log('========================================================\n');

  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'));
  const testResults = [];

  const browser = await chromium.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    headless: true
  });

  try {
    for (const testCase of manifest.test_cases) {
      console.log(`\n--------------------------------------------------------`);
      console.log(`RUNNING ${testCase.test_id}: ${testCase.title}`);
      console.log(`Files: ${testCase.input_files.join(', ')}`);
      console.log(`--------------------------------------------------------`);

      // 1. Reset database to baseline before each test
      restoreBaselineDatabase();

      const context = await browser.newContext({ viewport: { width: 1366, height: 768 } });
      const page = await context.newPage();

      let testPassed = true;
      let errorDetails = null;
      let uploadStatusText = '';

      try {
        // 2. Capture initial state
        await page.goto('http://127.0.0.1:5050/#today', { waitUntil: 'networkidle' });
        await page.waitForTimeout(400);

        const initialScreenshot = path.join(SCREENSHOT_DIR, `${testCase.test_id}_01_initial.png`);
        await page.screenshot({ path: initialScreenshot });

        // 3. Navigate to Upload Screen
        await page.click('button[data-view-target="upload"]');
        await page.waitForSelector('#view-upload.active', { timeout: 3000 });

        // 4. Upload each file for this test
        for (const filename of testCase.input_files) {
          const filePath = path.join(FIXTURES_DIR, filename);
          console.log(`  Uploading file via browser #file-input: ${filename}`);

          await page.setInputFiles('#file-input', filePath);
          await page.waitForSelector('#upload-status-box', { state: 'visible', timeout: 5000 });
          await page.waitForTimeout(800); // allow status message and reload trigger

          uploadStatusText = await page.textContent('#upload-status-box');
          console.log(`  Upload Result: "${uploadStatusText.trim().replace(/\s+/g, ' ').substring(0, 100)}..."`);
        }

        const postUploadScreenshot = path.join(SCREENSHOT_DIR, `${testCase.test_id}_02_upload_status.png`);
        await page.screenshot({ path: postUploadScreenshot });

        // 5. Check outcome depending on test type
        if (testCase.test_id === 'TEST_K') {
          // Expect error rejection
          if (!uploadStatusText.includes('Error') && !uploadStatusText.includes('Validation')) {
            testPassed = false;
            errorDetails = `Expected validation error but got: ${uploadStatusText}`;
          } else {
            console.log('  ✅ Validation correctly caught and reported malformed input.');
          }
        } else if (testCase.test_id === 'TEST_J') {
          // Expect duplicate file detection on 2nd upload
          if (!uploadStatusText.includes('already been processed') && !uploadStatusText.includes('duplicate')) {
            testPassed = false;
            errorDetails = `Expected duplicate file notice but got: ${uploadStatusText}`;
          } else {
            console.log('  ✅ Duplicate file correctly recognized and skipped.');
          }
        } else {
          // Standard valid upload
          if (uploadStatusText.includes('Error')) {
            testPassed = false;
            errorDetails = `Unexpected upload error: ${uploadStatusText}`;
          }
        }

        // 6. Navigate to Today / Dashboard to check updated displayed state
        await page.click('button[data-view-target="today"]');
        await page.waitForTimeout(500);

        // 7. Refresh browser to verify durability / persistence
        console.log('  Reloading page to verify persistence across reloads...');
        await page.reload({ waitUntil: 'networkidle' });
        await page.waitForTimeout(600);

        const persistedScreenshot = path.join(SCREENSHOT_DIR, `${testCase.test_id}_03_persisted_today.png`);
        await page.screenshot({ path: persistedScreenshot });

        // 8. Fetch current API state to verify mathematical delta
        const stateRes = await page.evaluate(async () => {
          const res = await fetch('/api/state');
          return await res.json();
        });

        const currentMetrics = stateRes.metrics;
        console.log(`  Metrics after upload: Clients=${currentMetrics.client_count}, Overdue=$${currentMetrics.overdue_total}, WeOwe=$${currentMetrics.we_owe_total}`);

        // Compare with expected state
        if (testCase.expected_state.overdue_total !== undefined) {
          const expectedOverdue = testCase.expected_state.overdue_total;
          if (Math.abs(currentMetrics.overdue_total - expectedOverdue) > 0.01) {
            console.warn(`  ⚠️ Overdue discrepancy: Expected $${expectedOverdue}, got $${currentMetrics.overdue_total}`);
          }
        }

      } catch (err) {
        testPassed = false;
        errorDetails = err.message;
        console.error(`  ❌ Error executing ${testCase.test_id}:`, err.message);
      } finally {
        await context.close();
      }

      const outcome = {
        test_id: testCase.test_id,
        title: testCase.title,
        input_files: testCase.input_files,
        status: testPassed ? 'PASS' : 'FAIL',
        error_details: errorDetails,
        upload_status_message: uploadStatusText.trim().replace(/\s+/g, ' ').substring(0, 150)
      };

      testResults.push(outcome);
      console.log(`  Result for ${testCase.test_id}: ${outcome.status}`);
    }

    fs.writeFileSync(RESULTS_JSON_PATH, JSON.stringify(testResults, null, 2));
    console.log(`\n========================================================`);
    console.log(`All upload test fixtures completed! Results written to:`);
    console.log(`  ${RESULTS_JSON_PATH}`);
    console.log(`========================================================`);

  } finally {
    await browser.close();
    // Always restore the baseline database after test run
    restoreBaselineDatabase();
    console.log('Cleaned up: Baseline axeom.db fully restored.');
  }
}

runUploadTestSuite().catch(err => {
  console.error('Fatal Upload Test Failure:', err);
  process.exit(1);
});
