// Regression: PIN authorization must execute the pending privileged action once.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

(async () => {
  let calls = 0;
  const elements = {
    'owner-auth-modal': { classList: { add() {}, remove() {} } },
    'owner-auth-error': { style: {} },
    'owner-pin-input': { value: 'correct-pin', focus() {} }
  };
  const document = {
    addEventListener() {},
    getElementById: (id) => elements[id] || null
  };
  const context = vm.createContext({
    document, console, window: {},
    setTimeout: (fn) => fn(),
    fetch: async (path) => {
      assert.ok(['/api/auth/owner-session', '/api/auth/owner-status'].includes(path));
      return { json: async () => ({ status: 'success', is_authorized: true }) };
    },
    alert: () => { throw Error('Unexpected alert') }
  });
  vm.runInContext(fs.readFileSync('static/js/app.js', 'utf8'), context);
  vm.runInContext('openOwnerAuthModal(async () => { globalThis.__completed = (globalThis.__completed || 0) + 1; })', context);
  await vm.runInContext('submitOwnerAuth()', context);
  calls = vm.runInContext('globalThis.__completed || 0', context);
  assert.equal(calls, 1, 'PIN success should invoke pending callback exactly once');
  await vm.runInContext('submitOwnerAuth()', context);
  calls = vm.runInContext('globalThis.__completed || 0', context);
  assert.equal(calls, 1, 'Pending callback must not run again');
  console.log('Owner authorization callback regression: PASS');
})().catch(e => { console.error(e); process.exitCode = 1; });
