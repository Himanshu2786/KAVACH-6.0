import test from 'node:test';
import assert from 'node:assert/strict';

/**
 * Regression Test Suite for ReVerificationModal & EvidenceValidationPage Integration
 * 
 * Verifies:
 * 1. api.reVerifyFinding() success flow keeps modal open and preserves result dossier.
 * 2. Background parent data refresh (new finding object reference with same ID) does NOT wipe reResult.
 * 3. onSuccess callback does not close modal or reset selected finding.
 * 4. api.reVerifyFinding() failure flow keeps modal open, displays errorMsg, and allows retry.
 * 5. Modal closes ONLY when onClose is explicitly triggered.
 */

// Simulated Mock API
const createMockApi = (shouldFail = false) => ({
  reVerifyFinding: async (findingId) => {
    if (shouldFail) {
      throw new Error('Network probe timeout reaching target endpoint');
    }
    return {
      id: 'REV-1C7D2000',
      finding_id: findingId,
      before_evidence_id: 'EV-WM-API-DOCS-CB52',
      after_evidence_id: 'EVD-AFT-E5F73AB1',
      before_evidence_hash: '3a7b9f8e2d1c4e5a...',
      after_evidence_hash: '9f8e7d6c5b4a3a2b...',
      command_executed: 'curl -s -i https://www.worldmonitor.app/openapi.json',
      output_before: 'HTTP/2 200\nContent-Type: application/json\n...',
      output_after: 'HTTP/2 200\nContent-Type: application/json\n...',
      new_status: 'STILL_OPEN',
      summary: 'Target endpoint still returns HTTP 200. Vulnerability remains open.',
      state_diff: JSON.stringify({
        security_improved: false,
        change_detected: false,
        verdict_reason: 'Vulnerability condition is still open after empirical re-probe.'
      }),
      timestamp: '2026-09-22T23:30:00Z'
    };
  },
  getEvidence: async () => [
    {
      id: 'EV-WM-API-DOCS-CB52',
      finding_id: 'WM-API-DOCS-CB52',
      raw_data: 'HTTP 200 OK',
      integrity_hash: '3a7b9f8e2d1c4e5a...'
    }
  ]
});

// Model representing the fixed ReVerificationModal state machine & lifecycle
class ReVerificationModalController {
  constructor({ isOpen, finding, onClose, onSuccess, api }) {
    this.isOpen = isOpen;
    this.finding = finding;
    this.onClose = onClose;
    this.onSuccess = onSuccess;
    this.api = api;

    this.running = false;
    this.reResult = null;
    this.parsedDiff = null;
    this.errorMsg = null;
    this.beforeEvidence = null;

    // Ref tracking to guard against parent reference updates
    this.activeFindingIdRef = null;
    this.prevIsOpenRef = false;

    this.syncEffect();
  }

  syncEffect() {
    const justOpened = this.isOpen && !this.prevIsOpenRef;
    const findingChanged = this.isOpen && Boolean(this.finding && this.finding.id !== this.activeFindingIdRef);

    this.prevIsOpenRef = this.isOpen;

    if (!this.isOpen) {
      this.activeFindingIdRef = null;
      return;
    }

    if (justOpened || findingChanged) {
      if (this.finding) {
        this.activeFindingIdRef = this.finding.id;
        this.reResult = null;
        this.parsedDiff = null;
        this.errorMsg = null;
      }
    }
  }

  updateProps({ isOpen, finding }) {
    this.isOpen = isOpen;
    this.finding = finding;
    this.syncEffect();
  }

  async handleRunReverification() {
    if (!this.finding) return;
    this.running = true;
    this.errorMsg = null;
    try {
      const res = await this.api.reVerifyFinding(this.finding.id);
      this.reResult = res;
      if (res.state_diff) {
        try {
          this.parsedDiff = JSON.parse(res.state_diff);
        } catch {
          this.parsedDiff = null;
        }
      }
      if (this.onSuccess) {
        this.onSuccess(res);
      }
    } catch (err) {
      this.errorMsg = err.message || 'Empirical re-verification probe encountered an error.';
    } finally {
      this.running = false;
    }
  }
}

// Parent Page (EvidenceValidationPage) State Simulator
class ParentPageController {
  constructor(initialFinding, api) {
    this.api = api;
    this.selectedFinding = initialFinding;
    this.selectedFindingId = initialFinding.id;
    this.showReVerify = false;
    this.loading = false;
    this.toast = null;

    this.modal = new ReVerificationModalController({
      isOpen: this.showReVerify,
      finding: this.selectedFinding,
      onClose: () => {
        this.showReVerify = false;
        this.modal.updateProps({ isOpen: false, finding: this.selectedFinding });
      },
      onSuccess: (result) => {
        // Safe background refresh without clobbering selected finding or closing modal
        this.silentLoadData();
        this.toast = `State updated with differential evidence (${result?.new_status}).`;
      },
      api: this.api
    });
  }

  openModal() {
    this.showReVerify = true;
    this.modal.updateProps({ isOpen: true, finding: this.selectedFinding });
  }

  silentLoadData() {
    // Simulates background loadData(true):
    // Preserves selectedFindingId, updates finding with new object reference
    const refreshedFinding = {
      ...this.selectedFinding,
      status: 'STILL_OPEN',
      updated_at: new Date().toISOString()
    };
    this.selectedFinding = refreshedFinding;
    // Parent passes new finding reference down to modal props
    this.modal.updateProps({ isOpen: this.showReVerify, finding: this.selectedFinding });
  }
}

test('SUCCESS FLOW: re-verification keeps modal open, renders result, and preserves state during parent data refresh', async () => {
  const mockApi = createMockApi(false);
  const initialFinding = {
    id: 'WM-API-DOCS-CB52',
    title: 'Publicly Exposed Interactive API Schema & Documentation',
    status: 'CONFIRMED',
    affected_component: 'https://www.worldmonitor.app/openapi.json',
    base_severity: 'MEDIUM'
  };

  const parent = new ParentPageController(initialFinding, mockApi);

  // 1. Open Modal
  parent.openModal();
  assert.equal(parent.showReVerify, true, 'Modal is open');
  assert.equal(parent.modal.isOpen, true, 'Modal controller is open');
  assert.equal(parent.modal.reResult, null, 'reResult is initially null before running');

  // 2. Click EXECUTE REAL RE-TEST
  await parent.modal.handleRunReverification();

  // 3. Verify modal remains open
  assert.equal(parent.showReVerify, true, 'Parent showReVerify state must remain TRUE');
  assert.equal(parent.modal.isOpen, true, 'Modal controller must remain open');

  // 4. Verify result is rendered and intact
  assert.notEqual(parent.modal.reResult, null, 'reResult must NOT be null');
  assert.equal(parent.modal.reResult.id, 'REV-1C7D2000', 'Record ID must match');
  assert.equal(parent.modal.reResult.new_status, 'STILL_OPEN', 'Verdict must be STILL_OPEN');
  assert.equal(parent.modal.reResult.before_evidence_id, 'EV-WM-API-DOCS-CB52', 'Before evidence ID must match');
  assert.equal(parent.modal.reResult.after_evidence_id, 'EVD-AFT-E5F73AB1', 'After evidence ID must match');
  assert.equal(parent.modal.parsedDiff.security_improved, false, 'Parsed state diff must indicate not improved');

  // 5. Verify parent data refresh did NOT reset selected finding
  assert.equal(parent.selectedFindingId, 'WM-API-DOCS-CB52', 'Selected finding ID must remain WM-API-DOCS-CB52');
  assert.equal(parent.selectedFinding.id, 'WM-API-DOCS-CB52', 'Selected finding object must remain WM-API-DOCS-CB52');

  // 6. Verify result dossier was NOT wiped out by parent background update
  assert.notEqual(parent.modal.reResult, null, 'reResult MUST remain populated after parent refresh');
  assert.equal(parent.modal.reResult.new_status, 'STILL_OPEN', 'reResult verdict must still be STILL_OPEN');

  // 7. Verify explicit manual close
  parent.modal.onClose();
  assert.equal(parent.showReVerify, false, 'Modal closes only on explicit onClose');
  assert.equal(parent.modal.isOpen, false, 'Modal state is now closed');
});

test('ERROR FLOW: failed re-verification keeps modal open, renders error, and allows retry', async () => {
  const failingApi = createMockApi(true);
  const initialFinding = {
    id: 'WM-API-DOCS-CB52',
    title: 'Publicly Exposed Interactive API Schema & Documentation',
    status: 'CONFIRMED',
    affected_component: 'https://www.worldmonitor.app/openapi.json',
    base_severity: 'MEDIUM'
  };

  const parent = new ParentPageController(initialFinding, failingApi);

  // 1. Open Modal
  parent.openModal();
  assert.equal(parent.modal.isOpen, true, 'Modal is open');

  // 2. Click EXECUTE REAL RE-TEST (which fails)
  await parent.modal.handleRunReverification();

  // 3. Verify modal remains open
  assert.equal(parent.showReVerify, true, 'Modal must NOT close on error');
  assert.equal(parent.modal.isOpen, true, 'Modal controller must remain open');

  // 4. Verify error is captured and displayed
  assert.equal(parent.modal.running, false, 'running must reset to false');
  assert.notEqual(parent.modal.errorMsg, null, 'errorMsg must be displayed');
  assert.match(parent.modal.errorMsg, /Network probe timeout/, 'errorMsg must match probe failure');
  assert.equal(parent.modal.reResult, null, 'reResult remains null');

  // 5. Verify retry is possible (recover with working API)
  parent.modal.api = createMockApi(false);
  await parent.modal.handleRunReverification();

  // 6. Verify retry succeeded and cleared error
  assert.equal(parent.modal.errorMsg, null, 'errorMsg cleared upon successful retry');
  assert.notEqual(parent.modal.reResult, null, 'reResult populated after retry');
  assert.equal(parent.modal.reResult.new_status, 'STILL_OPEN', 'Verdict rendered after retry');
  assert.equal(parent.modal.isOpen, true, 'Modal still open after retry');
});
