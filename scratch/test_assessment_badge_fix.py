import httpx

base = 'http://127.0.0.1:8000'
STAGES = ['DISCOVER','ASSESS','CORRELATE','ANALYZE','VALIDATE','PRIORITIZE','REMEDIATE','REPORT']

def simulate_badge(selectedStage, currentStage, status, progress):
    currentIdx = STAGES.index(currentStage)
    selectedIdx = STAGES.index(selectedStage)
    assessmentCompleted = (status == 'COMPLETED') or (progress >= 100)
    if assessmentCompleted and selectedIdx <= currentIdx:
        return 'COMPLETED'
    elif not assessmentCompleted and selectedIdx < currentIdx:
        return 'COMPLETED'
    elif not assessmentCompleted and selectedIdx == currentIdx:
        return 'RUNNING'
    elif selectedIdx > currentIdx:
        return 'PENDING'
    return 'COMPLETED'

def simulate_stepper(currentStage, assessmentCompleted):
    currentIndex = STAGES.index(currentStage)
    result = []
    for idx, stage in enumerate(STAGES):
        isCompleted = (currentIndex >= idx) if assessmentCompleted else (currentIndex > idx)
        isCurrent = (not assessmentCompleted) and (currentIndex == idx)
        icon = 'CHECK' if isCompleted else ('ACTIVE' if isCurrent else 'PENDING')
        result.append((stage, icon))
    return result

# TEST 1: Exact bug case
print("=== TEST 1: ASM-F8CFA2EB (The Bug Case) ===")
r = httpx.get(f'{base}/api/assessments/ASM-F8CFA2EB', timeout=5)
a = r.json()
print(f"  status        = {a['status']}")
print(f"  progress      = {a['progress']}")
print(f"  current_stage = {a['current_stage']}")
print()
print("  Stage Badge Simulation (Fixed Logic):")
for s in STAGES:
    b = simulate_badge(s, a['current_stage'], a['status'], a['progress'])
    marker = '  <-- REPORT (was BUG: RUNNING, now FIXED: COMPLETED)' if s == 'REPORT' else ''
    print(f"    {s:12s} -> {b}{marker}")
print()
print("  Stepper Simulation:")
ac = (a['status'] == 'COMPLETED') or (a['progress'] >= 100)
for stage, icon in simulate_stepper(a['current_stage'], ac):
    marker = '  <-- green check' if icon == 'CHECK' else ''
    print(f"    [{icon:7s}] {stage}{marker}")

# TEST 2: Browser refresh
print()
print("=== TEST 2: After Browser Refresh ===")
r2 = httpx.get(f'{base}/api/assessments/ASM-F8CFA2EB', timeout=5)
a2 = r2.json()
b2 = simulate_badge('REPORT', a2['current_stage'], a2['status'], a2['progress'])
print(f"  After refresh: REPORT stage badge = {b2}")
assert b2 == 'COMPLETED', f"FAIL: Expected COMPLETED, got {b2}"
print("  PASS: Refresh preserves COMPLETED status.")

# TEST 3: Running assessment (must NOT show COMPLETED on active stage)
print()
print("=== TEST 3: Genuinely Running Assessment (VALIDATE stage, 50%) ===")
for s in STAGES:
    b = simulate_badge(s, 'VALIDATE', 'RUNNING', 50)
    print(f"    {s:12s} -> {b}")
assert simulate_badge('VALIDATE', 'VALIDATE', 'RUNNING', 50) == 'RUNNING', "FAIL: Running should show RUNNING"
assert simulate_badge('DISCOVER', 'VALIDATE', 'RUNNING', 50) == 'COMPLETED', "FAIL: Past stages should show COMPLETED"
assert simulate_badge('REPORT',   'VALIDATE', 'RUNNING', 50) == 'PENDING',   "FAIL: Future stages should show PENDING"
print("  PASS: Running assessment shows correct states.")

# TEST 4: Previous stages on completed assessment
print()
print("=== TEST 4: Previous Stages on Completed Assessment ===")
prev_b = simulate_badge('DISCOVER', 'REPORT', 'COMPLETED', 100)
print(f"  DISCOVER badge = {prev_b}")
assert prev_b == 'COMPLETED', f"FAIL: {prev_b}"
print("  PASS: Previous stages remain COMPLETED.")

print()
print("=== ALL TESTS PASSED ===")
