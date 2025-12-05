# AI Workflow Shield - Architecture Deep Dive

## 🏗️ System Architecture

### Data Flow

```
┌─────────────────┐
│ Guardian Agent  │ (Local Python Agent)
│  - Collects     │
│  - Normalizes   │
│  - Batches      │
└────────┬────────┘
         │ HTTPS POST
         ▼
┌─────────────────┐
│ Ingestion API   │ (FastAPI)
│  - Validates    │
│  - Normalizes   │
│  - Stores       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Threat Engine  │ (Core Moat)
│  - Rules        │
│  - Patterns     │
│  - LLM Models   │
│  - Risk Score   │
└────────┬────────┘
         │
         ├─ Risk < 7 → Log & Continue
         │
         └─ Risk ≥ 7 → ▼
                    ┌──────────────┐
                    │   Incident   │
                    │   System     │
                    │  - Timeline  │
                    │  - RCA       │
                    │  - PDF       │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Pattern    │
                    │   Library    │
                    │  (Flywheel)  │
                    └──────────────┘
```

## 🔧 Component Details

### 1. Guardian Agent (`guardian-agent/`)

**Purpose:** Local telemetry collection agent

**Key Components:**
- `event_collector.py`: Collects and normalizes events
- `filesystem_watcher.py`: Monitors log files
- `tool_call_parser.py`: Parses tool usage
- `llm_output_parser.py`: Analyzes LLM outputs
- `batch_sender.py`: Sends events to cloud

**Event Types:**
- `tool_call`: Agent tool invocations
- `llm_completion`: LLM prompts/responses
- `api_access`: API calls
- `system_anomaly`: System-level issues

**Local Risk Assessment:**
- Lightweight heuristics
- Pattern matching
- Entropy checks
- Risk score: 0-10

### 2. Ingestion API (`backend/ingestion/`)

**Purpose:** Receive and store events

**Endpoints:**
- `POST /api/v1/ingest`: Receive event batches
- `GET /api/v1/health`: Health check

**Processing Pipeline:**
1. **Validation** (`validator.py`): Check event structure
2. **Normalization** (`normalizer.py`): Canonical form + PII cleaning
3. **Storage** (`storage.py`): Store in PostgreSQL
4. **Queueing**: Mark for threat engine processing

**Security:**
- API key authentication
- Token-based auth
- PII removal
- Event deduplication (hash-based)

### 3. Threat Engine (`backend/threat_engine/`)

**Purpose:** Core threat detection (THE MOAT)

#### 3.1 Rules-Based Detection (`rules/`)

**Modules:**
- `prompt_injection.py`: Detect injection attempts
- `jailbreaking.py`: Detect jailbreak attempts
- `tool_abuse.py`: Detect dangerous tool usage
- `api_abuse.py`: Detect unauthorized API access
- `output_drift.py`: Detect unexpected LLM behavior
- `entropy_check.py`: Detect encoded/encrypted content

**Scoring:** Each rule returns 0-10 risk score

#### 3.2 LLM-Based Detection (`models/`)

**Models:**
- `llm_analyzer.py`: Multi-model analysis (Gemini + GPT-4)
- `semantic_risk.py`: Embedding-based similarity
- `hallucination_detector.py`: Detect hallucinations
- `injection_detector.py`: Advanced injection detection

**Ensemble:** Consensus from multiple models

#### 3.3 Pattern Matching (`patterns/`)

**Database:** `pattern_list.json` (proprietary signatures)

**Categories:**
- Prompt injection variants
- Jailbreak sequences
- Tool abuse patterns
- Output drift signatures

**Matching:** Exact + regex matching

#### 3.4 Risk Scoring (`risk.py`)

**Formula:**
```
total_risk = (rules_risk * 0.4) + (pattern_risk * 0.3) + (model_risk * 0.3)
```

**Thresholds:**
- 0-3: Normal
- 4-6: Suspicious
- 7-10: Incident

#### 3.5 Processor (`processor.py`)

**Workflow:**
1. Calculate risk scores
2. Store risk analysis
3. Update event risk
4. Trigger incident if risk ≥ 7

### 4. Incident System (`incident/`)

**Purpose:** Handle security incidents

**Components:**
- `detector.py`: Detect and create incidents
- `timeline_builder.py`: Build event timeline
- `rca_generator.py`: Generate Root Cause Analysis (LLM-powered)
- `pdf_report.py`: Export PDF reports
- `incident_db.py`: Database operations

**Incident Lifecycle:**
1. **Detection**: High-risk event triggers incident
2. **Timeline**: Build 30-minute event window
3. **RCA**: LLM generates analysis
4. **PDF**: Export report
5. **Pattern Extraction**: Auto-extract new patterns (flywheel)

### 5. Threat Library (`patterns/`)

**Purpose:** Proprietary threat signature database

**Components:**
- `pattern_list.json`: Pattern database
- `matcher.py`: Pattern matching engine
- `updater.py`: Pattern management
- `scripts/auto_extract_patterns.py`: Auto-extraction from incidents

**Flywheel Effect:**
- New incidents → Extract patterns → Update library → Better detection

**Growth Metrics:**
- Number of patterns
- Match accuracy
- Coverage by category

### 6. Shared Utilities (`shared/`)

**Components:**
- `schemas/events.py`: Event schemas (Pydantic)
- `config.py`: Configuration management
- `logger.py`: Unified logging
- `pii_cleaner.py`: PII removal
- `token_auth.py`: Authentication
- `hashing.py`: Event hashing
- `schema.sql`: Database schema

## 🗄️ Database Schema

**Tables:**
- `workspaces`: Workspace management
- `agents`: Agent registration
- `events`: Event storage
- `patterns`: Threat patterns
- `pattern_matches`: Pattern match tracking
- `risk_scores`: Risk analysis storage
- `incidents`: Incident records
- `incident_events`: Incident-event associations

## 🔄 Processing Flow

### Event Processing

1. **Collection** (Guardian Agent)
   - Monitor filesystem
   - Parse logs
   - Collect events
   - Local risk assessment

2. **Ingestion** (API)
   - Validate events
   - Normalize format
   - Remove PII
   - Store in DB

3. **Threat Analysis** (Threat Engine)
   - Rules-based detection
   - Pattern matching
   - LLM analysis
   - Risk scoring

4. **Incident Handling** (Incident System)
   - Create incident
   - Build timeline
   - Generate RCA
   - Export PDF
   - Extract patterns

### Background Worker

`backend/worker.py` processes queued events:
- Polls for unprocessed events (`risk_engine IS NULL`)
- Processes through threat engine
- Triggers incidents as needed

## 🛡️ Moat Components

1. **Proprietary Patterns**: Grows with every customer
2. **Multi-Model Ensemble**: Gemini + GPT-4 consensus
3. **Behavior Models**: LLM-powered anomaly detection
4. **Auto-Extraction**: Incidents → Patterns → Better detection
5. **Cross-Customer Intelligence**: Shared patterns (anonymized)

## 📈 Scalability

**Horizontal Scaling:**
- Multiple ingestion API instances
- Multiple threat engine workers
- Database connection pooling
- Redis queue (optional)

**Performance:**
- Batch processing
- Async I/O
- Connection pooling
- Indexed queries

## 🔐 Security

- PII cleaning before storage
- Token-based authentication
- Event deduplication
- Secure API endpoints
- Database encryption (production)

## 🧪 Testing

**Unit Tests:**
- Rule detection
- Pattern matching
- Risk scoring
- Event parsing

**Integration Tests:**
- End-to-end event flow
- Incident creation
- Pattern extraction

**Synthetic Data:**
- `examples/synthetic_events.py`: Generate test events
- `examples/test_event_flow.py`: Test complete flow

## 🚀 Deployment

**Guardian Agent:**
- Install via `install.sh`
- Runs as systemd/launchd service
- Monitors local filesystem

**Backend:**
- FastAPI with uvicorn
- PostgreSQL database
- Background workers
- Optional: Redis queue

**Scaling:**
- Load balancer for API
- Multiple worker instances
- Database replication
- CDN for static assets

---

**This is the moat. This is defensible IP.**

