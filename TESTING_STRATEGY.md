# Testing Strategy for AgentG

## 🎯 Recommendation: Test First, UI Second

**Why?** The UI will be much more valuable once we know the backend works correctly. Testing first ensures:
- Data flows correctly end-to-end
- API endpoints return correct data
- UI will have real data to display
- We catch bugs before building UI around them

---

## 📋 Testing Phases

### Phase 1: Backend Unit Tests (Priority: CRITICAL)
**Goal:** Verify each component works in isolation

**What to Test:**
1. **Event Collection**
   - ✅ Event normalization
   - ✅ PII cleaning
   - ✅ Event hashing/deduplication

2. **Threat Engine**
   - ✅ Rules-based detection (all 6 rules)
   - ✅ Pattern matching
   - ✅ Risk scoring calculation
   - ⚠️ LLM analysis (mock responses for now)

3. **Compliance Engine**
   - ✅ HIPAA detector
   - ✅ GLBA detector
   - ✅ PCI detector
   - ✅ SOC2 detector
   - ✅ NIST detector
   - ✅ AI Act classifier
   - ✅ Compliance risk scoring

4. **Incident System**
   - ✅ Incident creation
   - ✅ Timeline building
   - ⚠️ RCA generation (mock for now)
   - ⚠️ PDF generation (test text output)

5. **Pattern Matching**
   - ✅ Pattern loading
   - ✅ Pattern matching logic
   - ✅ Pattern updates

**Estimated Time:** 2-3 days

---

### Phase 2: Integration Tests (Priority: HIGH)
**Goal:** Verify components work together

**What to Test:**
1. **Full Event Flow**
   ```
   Guardian Agent → Ingestion API → Threat Engine → Compliance Engine → Incident System
   ```

2. **API Endpoints**
   - ✅ `POST /api/v1/ingest` (with real events)
   - ✅ `GET /api/v1/compliance/summary`
   - ✅ `GET /api/v1/compliance/events`
   - ✅ `GET /api/v1/compliance/incidents`
   - ✅ `GET /api/v1/health`

3. **Database Integration**
   - ✅ Event storage
   - ✅ Risk score storage
   - ✅ Incident storage
   - ✅ Compliance mapping storage

**Estimated Time:** 1-2 days

---

### Phase 3: End-to-End Testing (Priority: HIGH)
**Goal:** Test complete workflows

**Test Scenarios:**

1. **Prompt Injection Detection**
   - Send event with injection attempt
   - Verify: Risk score > 7, Incident created, Compliance flags set

2. **PHI Leakage Detection**
   - Send event with medical data
   - Verify: HIPAA flag, Compliance risk, Evidence collected

3. **PCI Data Detection**
   - Send event with credit card number
   - Verify: PCI flag, High compliance risk, Incident triggered

4. **Multi-Event Incident**
   - Send multiple related suspicious events
   - Verify: Timeline built, RCA generated, Report created

**Estimated Time:** 1 day

---

### Phase 4: UI Development (Priority: MEDIUM)
**Goal:** Build Lovable UI to visualize data

**UI Components Needed:**

1. **Dashboard**
   - Risk score overview
   - Recent incidents
   - Compliance summary
   - Event timeline

2. **Events View**
   - List of events with filters
   - Risk scores
   - Compliance flags
   - Event details

3. **Incidents View**
   - List of incidents
   - Status (open/closed)
   - Severity
   - Timeline visualization

4. **Compliance Dashboard**
   - Standards overview (HIPAA, GLBA, PCI, etc.)
   - Violation counts
   - Risk levels
   - Evidence links

5. **Reports**
   - RCA viewer
   - Compliance reports
   - PDF download

**API Endpoints for UI:**
- `GET /api/v1/compliance/summary` ✅
- `GET /api/v1/compliance/events` ✅
- `GET /api/v1/compliance/incidents` ✅
- `GET /api/v1/compliance/report/{incident_id}` ✅
- `GET /api/v1/events` (need to add)
- `GET /api/v1/incidents` (need to add)
- `GET /api/v1/risk-scores` (need to add)

**Estimated Time:** 2-3 days

---

## 🧪 Testing Tools & Setup

### Test Framework
- **pytest** - Python testing framework
- **pytest-asyncio** - For async tests
- **httpx** - For API testing
- **pytest-mock** - For mocking

### Test Database
- Use **SQLite** for testing (faster, no setup)
- Or **PostgreSQL test database** (more realistic)

### Mock Services
- **LLM APIs** - Mock responses (don't call real APIs in tests)
- **File system** - Mock file operations
- **Time** - Mock timestamps for consistent tests

---

## 📝 Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── unit/
│   ├── test_event_collector.py
│   ├── test_threat_rules.py
│   ├── test_compliance_detectors.py
│   ├── test_pattern_matcher.py
│   └── test_risk_scorer.py
├── integration/
│   ├── test_ingestion_flow.py
│   ├── test_threat_engine_flow.py
│   ├── test_compliance_flow.py
│   └── test_incident_flow.py
├── e2e/
│   ├── test_prompt_injection.py
│   ├── test_phi_leakage.py
│   ├── test_pci_detection.py
│   └── test_multi_event_incident.py
└── api/
    ├── test_ingestion_api.py
    └── test_compliance_api.py
```

---

## 🚀 Quick Start Testing

### 1. Install Test Dependencies
```bash
pip install pytest pytest-asyncio httpx pytest-mock
```

### 2. Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_threat_rules.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### 3. Test Without Database
```bash
# Use SQLite in-memory database
export DATABASE_URL=sqlite:///:memory:
pytest
```

---

## ✅ Success Criteria

**Before Building UI:**
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] API endpoints return correct data
- [ ] Database operations work correctly
- [ ] At least 80% code coverage

**After UI is Built:**
- [ ] UI displays real data from backend
- [ ] All API endpoints work from UI
- [ ] Events flow correctly to UI
- [ ] Incidents appear in UI
- [ ] Compliance data displays correctly

---

## 🎯 Recommended Order

1. **Week 1: Testing**
   - Day 1-2: Unit tests
   - Day 3: Integration tests
   - Day 4: End-to-end tests
   - Day 5: Fix bugs, improve coverage

2. **Week 2: UI Development**
   - Day 1: API endpoint additions (if needed)
   - Day 2-3: Build Lovable UI
   - Day 4: Connect UI to backend
   - Day 5: Polish and test UI

---

## 💡 Why This Approach?

1. **Catch Bugs Early** - Find issues before building UI
2. **Better UI** - UI built on tested, reliable backend
3. **Faster Development** - Less debugging later
4. **Confidence** - Know system works before adding UI layer
5. **Documentation** - Tests serve as usage examples

---

## 🔗 Next Steps

1. Create test suite structure
2. Write unit tests for critical components
3. Write integration tests for API
4. Run end-to-end test scenarios
5. Build UI on Lovable once backend is tested

