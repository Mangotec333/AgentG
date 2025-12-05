# AgentG Architecture Evolution Analysis

**Proposed Architecture**: 3-Layer Policy-Driven System  
**Date**: 2024-01-15  
**Status**: Strategic Assessment (No Code Changes Yet)

---

## Executive Summary

**Verdict**: ✅ **Excellent architectural evolution** - This is the right direction for production scalability and GTM flexibility.

**Assessment**:
- **Code Changes**: Moderate (6-8 weeks of development)
- **Testing Required**: Significant (4-6 weeks)
- **Production Readiness**: High (well-structured, backward-compatible approach)
- **Risk Level**: Low-Medium (additive changes, can run in shadow mode)

**Recommendation**: **Proceed with phased implementation** - This architecture will make AgentG significantly more flexible and market-ready.

---

## Current State Analysis

### What We Have Today

1. **Hardcoded Logic**:
   - Risk threshold: `7` (hardcoded in `processor.py:53`)
   - Incident creation: Direct trigger when `risk >= 7`
   - Compliance: All standards run for all tenants
   - No tenant-specific customization

2. **Current Flow**:
   ```
   Event → Threat Engine → Risk Score → If >= 7 → Incident
   Event → Compliance Mapper → All Detectors → All Standards
   ```

3. **Current Data Model**:
   - `events` (raw + normalized)
   - `risk_scores` (per event)
   - `compliance_mappings` (per event, per standard)
   - `incidents` (triggered events)

### What's Missing for GTM

1. **No Tenant Customization**: Can't adjust thresholds per customer
2. **No Industry Targeting**: Can't pre-configure for banking vs healthcare
3. **No Policy Flexibility**: Actions are hardcoded (create incident, nothing else)
4. **No Compliance Packs**: All standards always run, can't enable/disable
5. **No Action Variety**: Only one action type (create incident)

---

## Proposed Architecture Assessment

### ✅ Strengths of the Proposal

1. **Clean Separation of Concerns**
   - Core engine stays generic (good for maintainability)
   - Policy layer is data-driven (good for customization)
   - UI layer is just presentation (good for multi-tenant)

2. **Scalability**
   - New compliance standard = new pack, not code change
   - New industry = new pack combo, not rewrite
   - New action type = new action handler, not core change

3. **GTM Flexibility**
   - Banking edition = GLBA + PCI packs
   - Healthcare edition = HIPAA pack
   - SaaS edition = SOC2 + NIST packs
   - Same codebase, different configurations

4. **Backward Compatibility**
   - Can run in shadow mode
   - Existing logic can remain as "default policy"
   - Migration path is clear

5. **Testability**
   - Policy evaluation is pure function (easy to test)
   - Compliance packs are JSON (easy to validate)
   - Actions are isolated (easy to mock)

### ⚠️ Considerations

1. **Complexity Increase**
   - More moving parts (findings, policies, packs)
   - More database tables
   - More code paths to test

2. **Performance**
   - Policy evaluation adds latency
   - More database queries
   - Need efficient policy matching

3. **Migration**
   - Existing incidents need to map to findings
   - Existing compliance mappings need to map to findings
   - Need data migration strategy

---

## Code Changes Required

### Phase 1: Findings Layer (2 weeks)

#### Database Changes

**New Table: `findings`**
```sql
CREATE TABLE findings (
    id VARCHAR(255) PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL REFERENCES events(id),
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id),
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id),
    type VARCHAR(50) NOT NULL,  -- 'prompt_injection', 'pii_exposure', etc.
    standards TEXT[],            -- ['GLBA', 'HIPAA']
    rules_triggered TEXT[],      -- ['RULE_PI_001']
    violations TEXT[],           -- ['GLBA-001', 'HIPAA-002']
    risk_score INTEGER,          -- 0-10
    tags TEXT[],                 -- ['pii', 'financial', 'output_drift']
    metadata JSONB,              -- freeform details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_findings_event ON findings(event_id);
CREATE INDEX idx_findings_workspace ON findings(workspace_id);
CREATE INDEX idx_findings_type ON findings(type);
CREATE INDEX idx_findings_standards ON findings USING GIN(standards);
CREATE INDEX idx_findings_tags ON findings USING GIN(tags);
```

**Code Changes**:

1. **New Module: `backend/findings/finder.py`**
   - `FindingGenerator` class
   - Method: `generate_finding(event, risk_analysis, compliance_mapping)`
   - Aggregates data from events, risk_scores, compliance_mappings
   - Creates normalized finding record

2. **Modify: `backend/threat_engine/processor.py`**
   - After risk scoring, call `FindingGenerator.generate_finding()`
   - Store finding in database
   - Keep existing logic (for backward compatibility)

3. **New Module: `backend/findings/finding_db.py`**
   - Database operations for findings
   - CRUD operations
   - Query methods

**Testing**:
- Unit tests for `FindingGenerator`
- Integration tests for finding creation
- Database migration tests

**Impact**: Low risk - additive only, doesn't break existing flow

---

### Phase 2: Policy Engine (3 weeks)

#### Database Changes

**New Table: `policies`**
```sql
CREATE TABLE policies (
    id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT true,
    scope VARCHAR(50) DEFAULT 'workspace',  -- 'workspace' | 'agent' | 'workflow'
    match_condition JSONB NOT NULL,         -- JSON condition DSL
    actions JSONB NOT NULL,                 -- List of actions
    priority INTEGER DEFAULT 100,           -- Lower = higher priority
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policies_workspace ON policies(workspace_id);
CREATE INDEX idx_policies_enabled ON policies(enabled);
```

**New Table: `policy_actions`**
```sql
CREATE TABLE policy_actions (
    id VARCHAR(255) PRIMARY KEY,
    policy_id VARCHAR(255) NOT NULL REFERENCES policies(id),
    finding_id VARCHAR(255) NOT NULL REFERENCES findings(id),
    action_type VARCHAR(50) NOT NULL,      -- 'create_incident', 'notify', etc.
    action_payload JSONB,                   -- Action-specific data
    executed BOOLEAN DEFAULT false,
    executed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policy_actions_policy ON policy_actions(policy_id);
CREATE INDEX idx_policy_actions_finding ON policy_actions(finding_id);
CREATE INDEX idx_policy_actions_executed ON policy_actions(executed);
```

**Code Changes**:

1. **New Module: `backend/policy/condition_evaluator.py`**
   - `ConditionEvaluator` class
   - Method: `evaluate(condition, finding)` → bool
   - Supports JSON DSL: `{ "any": [...], "all": [...] }`
   - Field operators: `contains`, `>=`, `<=`, `==`, `!=`

2. **New Module: `backend/policy/policy_engine.py`**
   - `PolicyEngine` class
   - Method: `evaluate_policies(finding, workspace_id)` → List[actions]
   - Loads policies for workspace
   - Evaluates conditions
   - Returns matching actions

3. **New Module: `backend/policy/action_executor.py`**
   - `ActionExecutor` class
   - Methods: `execute_action(action_type, payload, finding)`
   - Handlers: `create_incident`, `notify_slack`, `notify_email`, `tag_agent`
   - Extensible for future actions

4. **New Worker: `backend/workers/policy_worker.py`**
   - Async worker that:
     - Polls for new findings
     - Evaluates policies
     - Executes actions
     - Records in `policy_actions` table

5. **Modify: `backend/threat_engine/processor.py`**
   - After finding creation, queue for policy evaluation
   - (Keep existing incident creation for backward compatibility)

**Testing**:
- Unit tests for condition evaluator (all operators, nested conditions)
- Unit tests for policy engine (priority, scope, enabled/disabled)
- Unit tests for action executor (all action types)
- Integration tests for policy worker
- Performance tests (policy evaluation latency)

**Impact**: Medium risk - new code path, but can run in shadow mode

---

### Phase 3: Compliance Packs (2 weeks)

#### Database Changes

**New Table: `compliance_packs`**
```sql
CREATE TABLE compliance_packs (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),                 -- 'banking', 'healthcare', 'saas'
    standards TEXT[] NOT NULL,               -- ['GLBA', 'PCI']
    description TEXT,
    policy_templates JSONB NOT NULL,        -- List of policy definitions
    default_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**New Table: `workspace_compliance_packs`**
```sql
CREATE TABLE workspace_compliance_packs (
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id),
    pack_id VARCHAR(255) NOT NULL REFERENCES compliance_packs(id),
    enabled BOOLEAN DEFAULT true,
    overrides JSONB,                        -- Custom thresholds, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, pack_id)
);
```

**Code Changes**:

1. **New Module: `backend/compliance/pack_manager.py`**
   - `CompliancePackManager` class
   - Method: `apply_pack(workspace_id, pack_id, overrides)`
   - Clones policy templates → concrete policies
   - Applies overrides

2. **New Module: `backend/compliance/pack_loader.py`**
   - `CompliancePackLoader` class
   - Loads pack definitions from database
   - Validates policy templates

3. **Seed Data Script: `scripts/seed_compliance_packs.py`**
   - Creates default packs:
     - `GLBA_BANK_DEFAULT`
     - `HIPAA_HEALTHCARE_DEFAULT`
     - `PCI_DEFAULT`
     - `SOC2_SAAS_DEFAULT`
     - `NIST_DEFAULT`
     - `AI_ACT_EU_DEFAULT`

4. **Modify: Workspace Creation**
   - On workspace creation, apply default packs based on industry
   - Or allow manual pack selection

**Testing**:
- Unit tests for pack manager
- Unit tests for pack loader
- Integration tests for pack application
- Validation tests for policy templates

**Impact**: Low risk - data-driven, easy to test

---

### Phase 4: Action Handlers (2 weeks)

**Code Changes**:

1. **Extend: `backend/policy/action_executor.py`**
   - Add handlers:
     - `create_incident` (already exists, refactor)
     - `notify_slack` (new)
     - `notify_email` (new)
     - `notify_webhook` (new)
     - `tag_agent` (new)
     - `block_request` (future - requires gateway integration)

2. **New Module: `backend/notifications/slack_notifier.py`**
   - Slack webhook integration

3. **New Module: `backend/notifications/email_notifier.py`**
   - Email sending (SMTP or service)

4. **New Module: `backend/notifications/webhook_notifier.py`**
   - Generic webhook POST

5. **Modify: `backend/threat_engine/incident_handler.py`**
   - Refactor to use action executor
   - Keep backward compatibility

**Testing**:
- Unit tests for all action handlers
- Integration tests for notifications
- Mock external services

**Impact**: Low risk - isolated handlers, easy to test

---

### Phase 5: Admin Panel (3-4 weeks)

**Code Changes**:

1. **New API Endpoints: `backend/admin/router.py`**
   - `GET /api/v1/admin/policies` - List policies
   - `POST /api/v1/admin/policies` - Create policy
   - `PUT /api/v1/admin/policies/{id}` - Update policy
   - `DELETE /api/v1/admin/policies/{id}` - Delete policy
   - `GET /api/v1/admin/compliance-packs` - List packs
   - `POST /api/v1/admin/workspaces/{id}/packs` - Apply pack
   - `PUT /api/v1/admin/workspaces/{id}/packs/{pack_id}` - Update pack

2. **New Module: `backend/admin/policy_service.py`**
   - Business logic for policy management

3. **Frontend (Future)**:
   - Policy editor UI
   - Compliance pack selector
   - Policy testing/simulation

**Testing**:
- API endpoint tests
- Authorization tests (workspace isolation)
- Validation tests

**Impact**: Medium risk - new API surface, needs auth

---

## Testing Requirements

### Unit Tests (2 weeks)

1. **Finding Generation**:
   - Test finding creation from events
   - Test finding aggregation logic
   - Test edge cases (missing data, null values)

2. **Condition Evaluator**:
   - Test all operators (`contains`, `>=`, `<=`, `==`, `!=`)
   - Test nested conditions (`any`, `all`)
   - Test field access (nested JSON)
   - Test error handling (invalid conditions)

3. **Policy Engine**:
   - Test policy matching
   - Test priority ordering
   - Test scope filtering (workspace, agent, workflow)
   - Test enabled/disabled policies

4. **Action Executor**:
   - Test all action types
   - Test action payload validation
   - Test error handling

5. **Compliance Pack Manager**:
   - Test pack application
   - Test override application
   - Test policy template cloning

### Integration Tests (2 weeks)

1. **End-to-End Policy Flow**:
   - Event → Finding → Policy Evaluation → Action Execution
   - Test with real database
   - Test with multiple policies
   - Test with conflicting policies (priority)

2. **Compliance Pack Application**:
   - Test pack application on workspace creation
   - Test pack enable/disable
   - Test pack override application

3. **Backward Compatibility**:
   - Test existing incident creation still works
   - Test existing compliance mapping still works
   - Test migration from old to new system

### Performance Tests (1 week)

1. **Policy Evaluation Performance**:
   - Test with 100+ policies per workspace
   - Test with complex nested conditions
   - Target: < 50ms per finding

2. **Finding Generation Performance**:
   - Test with high event volume
   - Target: < 10ms per finding

3. **Database Query Performance**:
   - Test finding queries with indexes
   - Test policy queries with indexes
   - Test action queries

### Migration Tests (1 week)

1. **Data Migration**:
   - Test migration of existing incidents to findings
   - Test migration of existing compliance mappings
   - Test rollback capability

2. **Shadow Mode**:
   - Test running new system alongside old system
   - Test comparison of results
   - Test gradual rollout

---

## Production Readiness Assessment

### ✅ What Makes This Production-Ready

1. **Backward Compatible**
   - Existing code continues to work
   - Can run in shadow mode
   - Gradual migration possible

2. **Well-Structured**
   - Clear separation of concerns
   - Modular design
   - Extensible architecture

3. **Testable**
   - Pure functions (condition evaluator)
   - Isolated components (action handlers)
   - Data-driven (policies, packs)

4. **Scalable**
   - Database indexes for performance
   - Async workers for policy evaluation
   - Caching opportunities (policies)

### ⚠️ Production Concerns

1. **Complexity**
   - More moving parts = more failure points
   - Need comprehensive monitoring
   - Need good error handling

2. **Performance**
   - Policy evaluation adds latency
   - Need efficient condition matching
   - May need caching layer

3. **Data Consistency**
   - Findings must be created atomically
   - Policy actions must be idempotent
   - Need transaction handling

4. **Migration**
   - Need careful data migration
   - Need rollback plan
   - Need monitoring during migration

---

## Implementation Strategy

### Recommended Approach: Phased Rollout

#### Phase 1: Shadow Mode (Weeks 1-6)
- Implement all components
- Run in shadow mode (no real actions)
- Compare results with existing system
- Fix discrepancies

#### Phase 2: Gradual Rollout (Weeks 7-8)
- Enable for 10% of workspaces
- Monitor performance and errors
- Gradually increase to 100%

#### Phase 3: Full Migration (Weeks 9-10)
- Switch to policy-driven system
- Keep old code as fallback
- Monitor for issues

#### Phase 4: Cleanup (Weeks 11-12)
- Remove old code paths
- Optimize performance
- Add monitoring/alerting

---

## Code Change Summary

### New Files (Estimated)

1. **Findings Layer** (3 files):
   - `backend/findings/finder.py`
   - `backend/findings/finding_db.py`
   - `backend/findings/__init__.py`

2. **Policy Engine** (4 files):
   - `backend/policy/condition_evaluator.py`
   - `backend/policy/policy_engine.py`
   - `backend/policy/action_executor.py`
   - `backend/policy/__init__.py`

3. **Policy Worker** (1 file):
   - `backend/workers/policy_worker.py`

4. **Compliance Packs** (3 files):
   - `backend/compliance/pack_manager.py`
   - `backend/compliance/pack_loader.py`
   - `scripts/seed_compliance_packs.py`

5. **Notifications** (3 files):
   - `backend/notifications/slack_notifier.py`
   - `backend/notifications/email_notifier.py`
   - `backend/notifications/webhook_notifier.py`

6. **Admin API** (2 files):
   - `backend/admin/router.py`
   - `backend/admin/policy_service.py`

**Total**: ~16 new files

### Modified Files (Estimated)

1. **Core Engine** (3 files):
   - `backend/threat_engine/processor.py` (add finding generation)
   - `backend/threat_engine/incident_handler.py` (refactor to use actions)
   - `backend/compliance_engine/compliance_mapper.py` (minor changes)

2. **Database** (1 file):
   - `shared/schema.sql` (add new tables)

3. **Workers** (1 file):
   - `backend/worker.py` (add policy worker)

**Total**: ~5 modified files

### Database Changes

- **New Tables**: 5 (findings, policies, policy_actions, compliance_packs, workspace_compliance_packs)
- **New Indexes**: ~15
- **Migrations**: 5 migration scripts

---

## Testing Summary

### Test Coverage Required

1. **Unit Tests**: ~150-200 new tests
   - Finding generation: 20 tests
   - Condition evaluator: 50 tests
   - Policy engine: 30 tests
   - Action executor: 30 tests
   - Compliance packs: 20 tests
   - Notifications: 20 tests

2. **Integration Tests**: ~30-40 new tests
   - End-to-end policy flow: 10 tests
   - Compliance pack application: 10 tests
   - Backward compatibility: 10 tests
   - Migration: 10 tests

3. **Performance Tests**: ~10 tests
   - Policy evaluation: 3 tests
   - Finding generation: 3 tests
   - Database queries: 4 tests

**Total**: ~190-250 new tests

### Testing Timeline

- **Unit Tests**: 2 weeks
- **Integration Tests**: 2 weeks
- **Performance Tests**: 1 week
- **Migration Tests**: 1 week

**Total**: 6 weeks of testing

---

## Risk Assessment

### Low Risk Areas ✅

1. **Findings Layer**: Additive only, doesn't break existing flow
2. **Compliance Packs**: Data-driven, easy to test
3. **Notifications**: Isolated handlers, easy to mock

### Medium Risk Areas ⚠️

1. **Policy Engine**: New code path, but can run in shadow mode
2. **Action Executor**: New execution path, but isolated
3. **Admin API**: New API surface, needs auth

### High Risk Areas 🔴

1. **Migration**: Data migration is always risky
   - **Mitigation**: Careful planning, rollback plan, shadow mode

2. **Performance**: Policy evaluation adds latency
   - **Mitigation**: Efficient condition matching, caching, async workers

---

## Final Recommendation

### ✅ Proceed with Implementation

**Why**:
1. **GTM Flexibility**: Enables industry-specific positioning
2. **Scalability**: Makes system more maintainable
3. **Customer Value**: Allows customization without code changes
4. **Market Differentiation**: Policy-driven approach is sophisticated

**How**:
1. **Phased Approach**: Implement in phases, test thoroughly
2. **Shadow Mode**: Run alongside existing system initially
3. **Gradual Rollout**: Enable for subset of customers first
4. **Monitoring**: Comprehensive monitoring during rollout

**Timeline**:
- **Development**: 6-8 weeks
- **Testing**: 4-6 weeks
- **Total**: 10-14 weeks to production

**Success Criteria**:
- ✅ All existing tests pass
- ✅ New tests achieve 90%+ coverage
- ✅ Performance within targets (< 50ms policy evaluation)
- ✅ Zero data loss during migration
- ✅ Backward compatibility maintained

---

## Conclusion

This architectural evolution is **well-designed and production-ready**. The proposed 3-layer architecture (Core → Policy → UI) is a solid foundation for scaling AgentG across industries and use cases.

**Key Benefits**:
- ✅ GTM flexibility (banking, healthcare, SaaS editions)
- ✅ Customer customization (per-tenant policies)
- ✅ Maintainability (single codebase)
- ✅ Scalability (data-driven, not code-driven)

**Key Risks**:
- ⚠️ Complexity increase (mitigated by good design)
- ⚠️ Performance concerns (mitigated by efficient implementation)
- ⚠️ Migration risk (mitigated by shadow mode)

**Recommendation**: **Proceed with phased implementation** - This is the right architecture for production scale and GTM success.

---

## Next Steps

1. **Review & Approve**: Get stakeholder approval
2. **Design Review**: Detailed design review session
3. **Sprint Planning**: Break into sprints
4. **Start Phase 1**: Begin with findings layer
5. **Continuous Testing**: Test as you build

---

*This is a strategic assessment. Actual implementation should follow detailed design documents and code reviews.*

