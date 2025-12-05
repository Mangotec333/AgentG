# Test Runner UI Plan - Lovable

## 🎯 Goal
Build a simple, friendly UI for:
- ✅ Running test cases with one click
- ✅ Viewing test results visually
- ✅ Seeing what's happening in real-time
- ✅ Not a full production dashboard (that comes later)

---

## 🖥️ UI Components Needed

### 1. Test Suite Selector
**Simple dropdown/buttons:**
- Unit Tests
- Integration Tests
- End-to-End Tests
- Run All Tests

### 2. Test Runner Panel
**Shows:**
- Current test running
- Progress bar
- Real-time output/logs
- Pass/Fail status

### 3. Results Display
**After tests complete:**
- ✅ Passed tests (green)
- ❌ Failed tests (red)
- ⚠️ Warnings (yellow)
- 📊 Summary stats (total, passed, failed, coverage)

### 4. Test Details View
**Click on a test to see:**
- Test name
- Status (pass/fail)
- Execution time
- Error message (if failed)
- Assertions that passed/failed

### 5. Quick Actions
**Buttons:**
- Run Selected Test
- Run All Tests
- Clear Results
- Export Results (JSON/CSV)

---

## 🔌 Backend API Needed

### Test Runner Endpoint
```python
POST /api/v1/tests/run
{
  "test_type": "unit" | "integration" | "e2e" | "all",
  "test_names": ["test_prompt_injection", ...]  # optional, specific tests
}

Response:
{
  "test_run_id": "uuid",
  "status": "running" | "completed" | "failed",
  "results": [...]
}
```

### Test Status Endpoint
```python
GET /api/v1/tests/status/{test_run_id}

Response:
{
  "status": "running",
  "progress": 0.65,
  "current_test": "test_prompt_injection",
  "completed": 10,
  "total": 20
}
```

### Test Results Endpoint
```python
GET /api/v1/tests/results/{test_run_id}

Response:
{
  "test_run_id": "uuid",
  "status": "completed",
  "summary": {
    "total": 50,
    "passed": 45,
    "failed": 5,
    "coverage": 82.5
  },
  "results": [
    {
      "test_name": "test_prompt_injection",
      "status": "passed",
      "duration": 0.123,
      "assertions": 5
    },
    {
      "test_name": "test_phi_leakage",
      "status": "failed",
      "duration": 0.456,
      "error": "AssertionError: Expected HIPAA flag but got None",
      "assertions": 3
    }
  ]
}
```

---

## 🎨 UI Design (Simple & Clean)

### Layout
```
┌─────────────────────────────────────────────────┐
│  🧪 AgentG Test Runner                          │
├─────────────────────────────────────────────────┤
│                                                  │
│  [Unit Tests] [Integration] [E2E] [Run All]    │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Running: test_prompt_injection           │  │
│  │ ████████████░░░░░░░░ 60%                │  │
│  │                                          │  │
│  │ ✅ test_event_collector (0.12s)         │  │
│  │ ✅ test_threat_rules (0.34s)            │  │
│  │ ⏳ test_prompt_injection (running...)   │  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  Results:                                       │
│  ┌──────────────────────────────────────────┐  │
│  │ Total: 50  ✅ Passed: 45  ❌ Failed: 5 │  │
│  │ Coverage: 82.5%                         │  │
│  │                                          │  │
│  │ ❌ test_phi_leakage                      │  │
│  │    Error: Expected HIPAA flag...        │  │
│  │    [View Details]                       │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Implementation Steps

### Step 1: Create Test Runner Backend
**File:** `backend/test_runner/api.py`

```python
from fastapi import APIRouter
import subprocess
import json
import uuid

router = APIRouter(prefix="/api/v1/tests", tags=["tests"])

@router.post("/run")
async def run_tests(test_type: str, test_names: List[str] = None):
    """Run pytest tests and return results."""
    test_run_id = str(uuid.uuid4())
    
    # Build pytest command
    if test_type == "all":
        cmd = ["pytest", "-v", "--json-report", "--json-report-file=/tmp/results.json"]
    elif test_type == "unit":
        cmd = ["pytest", "tests/unit/", "-v", "--json-report"]
    # ... etc
    
    # Run tests in background
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return {"test_run_id": test_run_id, "status": "running"}

@router.get("/results/{test_run_id}")
async def get_results(test_run_id: str):
    """Get test results."""
    # Read from JSON report
    with open(f"/tmp/results_{test_run_id}.json") as f:
        results = json.load(f)
    return results
```

### Step 2: Build Lovable UI
**Components:**
1. **TestRunner.tsx** - Main component
2. **TestResults.tsx** - Results display
3. **TestProgress.tsx** - Progress bar
4. **TestCard.tsx** - Individual test card

**Features:**
- Click button → Run tests
- Poll `/api/v1/tests/status/{id}` for progress
- Display results in cards
- Color-coded (green=pass, red=fail)
- Expandable details

### Step 3: Connect to Backend
- API calls to test runner endpoints
- Real-time updates (polling every 1-2 seconds)
- Error handling
- Loading states

---

## 📋 Minimal Test Suite to Create First

### Priority Tests (for UI to run):

1. **Unit Tests:**
   - `test_prompt_injection_detection`
   - `test_phi_leakage_detection`
   - `test_pci_data_detection`
   - `test_risk_scoring`

2. **Integration Tests:**
   - `test_ingestion_flow`
   - `test_threat_engine_flow`
   - `test_compliance_flow`

3. **E2E Tests:**
   - `test_prompt_injection_to_incident`
   - `test_phi_leakage_to_hipaa_flag`

---

## 🎯 Benefits of This Approach

✅ **Quick to Build** - Simple UI, focused on testing
✅ **Immediate Value** - See what works, what doesn't
✅ **User Friendly** - Click, see results, no CLI needed
✅ **Foundation** - Can expand to full dashboard later
✅ **Visual Feedback** - See tests running, results clearly

---

## 🔄 Workflow

1. **User clicks "Run Unit Tests"**
2. **Backend starts pytest**
3. **UI polls for status** (every 1-2 seconds)
4. **UI shows progress** (which test, progress bar)
5. **When done, show results** (pass/fail, errors, coverage)
6. **User can click test** to see details

---

## 📝 Next Steps

1. ✅ Create test runner backend API
2. ✅ Write minimal test suite (10-15 key tests)
3. ✅ Build Lovable UI (simple, focused)
4. ✅ Connect UI to backend
5. ✅ Test the test runner! 🎉

---

## 🎨 UI Mockup (Text)

```
╔═══════════════════════════════════════════════════╗
║  🧪 AgentG Test Runner                    [⚙️]  ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  Test Suite:                                     ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐        ║
║  │  Unit    │ │Integration│ │   E2E    │        ║
║  │  Tests   │ │  Tests    │ │  Tests   │        ║
║  └──────────┘ └──────────┘ └──────────┘        ║
║  ┌──────────────────────────────────────┐        ║
║  │        [▶️ Run All Tests]            │        ║
║  └──────────────────────────────────────┘        ║
║                                                   ║
║  ┌───────────────────────────────────────────┐ ║
║  │ Status: Running...                         │ ║
║  │ ████████████░░░░░░░░ 60%                   │ ║
║  │ Current: test_prompt_injection            │ ║
║  │ Completed: 6/10                            │ ║
║  └───────────────────────────────────────────┘ ║
║                                                   ║
║  Results:                                       ║
║  ┌───────────────────────────────────────────┐ ║
║  │ ✅ test_event_collector       0.12s       │ ║
║  │ ✅ test_threat_rules           0.34s       │ ║
║  │ ✅ test_pattern_matching       0.21s       │ ║
║  │ ❌ test_phi_leakage            0.45s       │ ║
║  │    ⚠️  Expected HIPAA flag but got None    │ ║
║  │ ✅ test_pci_detection          0.18s       │ ║
║  └───────────────────────────────────────────┘ ║
║                                                   ║
║  Summary:                                        ║
║  Total: 10  ✅ Passed: 9  ❌ Failed: 1          ║
║  Coverage: 85.2%                                 ║
╚═══════════════════════════════════════════════════╝
```

---

This is much simpler than a full dashboard - just focused on running tests and seeing results! 🎯

