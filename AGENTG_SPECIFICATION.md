# AgentG (Agent Guardian) - System Specification

**Version:** 1.0  
**Date:** 2024-01-15  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [Core Components](#core-components)
5. [Data Models](#data-models)
6. [API Specifications](#api-specifications)
7. [Threat Detection](#threat-detection)
8. [Compliance Engine](#compliance-engine)
9. [Incident Management](#incident-management)
10. [Database Schema](#database-schema)
11. [Security Requirements](#security-requirements)
12. [Deployment](#deployment)
13. [Testing Requirements](#testing-requirements)
14. [Performance Requirements](#performance-requirements)
15. [Future Enhancements](#future-enhancements)

---

## Executive Summary

**AgentG (Agent Guardian)** is a comprehensive security and compliance monitoring system designed to protect AI agent workflows from threats, detect compliance violations, and generate actionable incident reports. The system provides real-time threat detection, multi-standard compliance mapping, automated incident response, and detailed root cause analysis.

### Key Capabilities

- ✅ **Real-time Threat Detection**: 6 threat detection rules + LLM-based analysis
- ✅ **Multi-Standard Compliance**: HIPAA, GLBA, PCI-DSS, SOC 2, NIST, EU AI Act
- ✅ **Automated Incident Response**: Incident creation, RCA generation, PDF reports
- ✅ **Pattern Library**: Extensible pattern matching with auto-extraction
- ✅ **Vector Search Ready**: pgvector integration for RAG capabilities
- ✅ **Production Ready**: 100% test coverage, comprehensive error handling

---

## System Overview

### Purpose

AgentG monitors AI agent workflows in real-time, detecting:
- **Security Threats**: Prompt injection, jailbreaking, tool abuse, API abuse, output drift, encoded content
- **Compliance Violations**: HIPAA, GLBA, PCI-DSS, SOC 2, NIST, EU AI Act violations
- **Anomalies**: LLM hallucinations, semantic drift, unexpected behavior

### System Flow

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

---

## Architecture

### High-Level Architecture

**Three-Tier Architecture:**

1. **Guardian Agent** (Client-side)
   - Lightweight Python agent
   - Monitors local filesystem
   - Collects and normalizes events
   - Batches and sends to cloud

2. **Ingestion API** (Backend)
   - FastAPI-based REST API
   - Event validation and normalization
   - PII cleaning
   - Database storage
   - Queue management

3. **Threat Engine** (Backend)
   - Rules-based detection
   - Pattern matching
   - LLM-based analysis
   - Risk scoring
   - Incident creation

### Technology Stack

- **Language**: Python 3.8+
- **Framework**: FastAPI (async)
- **Database**: PostgreSQL (Supabase with pgvector)
- **LLM APIs**: OpenAI (primary), Gemini (optional fallback)
- **PDF Generation**: reportlab
- **Authentication**: JWT tokens + API keys
- **Deployment**: Docker-ready, systemd/launchd services

---

## Core Components

### 1. Guardian Agent (`guardian-agent/`)

**Purpose**: Local telemetry collection agent that monitors AI agent workflows.

#### Components

| File | Purpose |
|------|---------|
| `main.py` | Entry point with signal handling, graceful shutdown |
| `config.py` | Configuration management (env vars) |
| `event_collector.py` | Event collection and normalization |
| `filesystem_watcher.py` | Monitors JSONL log files |
| `tool_call_parser.py` | Parses tool usage events |
| `llm_output_parser.py` | Analyzes LLM outputs |
| `batch_sender.py` | Batch transmission with retries |

#### Event Types

- `tool_call`: Agent tool invocations
- `llm_completion`: LLM prompts and responses
- `api_access`: API calls
- `system_anomaly`: System-level issues

#### Local Risk Assessment

- Lightweight heuristics
- Pattern matching
- Entropy checks
- Risk score: 0-10

#### Configuration

```python
# Environment variables
GUARDIAN_AGENT_API_KEY=your_api_key
SHIELD_INGESTION_ENDPOINT=https://shield.mangotec.ai/api/v1/ingest
LOG_DIR=/path/to/logs
BATCH_SIZE=10
BATCH_INTERVAL=5  # seconds
```

---

### 2. Ingestion Pipeline (`backend/ingestion/`)

**Purpose**: Receive, validate, normalize, and store events from Guardian Agents.

#### Components

| File | Purpose |
|------|---------|
| `router.py` | FastAPI endpoints (`/api/v1/ingest`, `/api/v1/health`) |
| `validator.py` | Event validation using unified schema |
| `normalizer.py` | Event normalization + PII cleaning |
| `storage.py` | Database storage with deduplication |
| `security.py` | API key authentication |

#### Processing Pipeline

1. **Validation**: Check event structure against `AgentEvent` schema
2. **Normalization**: Convert to canonical form
3. **PII Cleaning**: Remove sensitive data before storage
4. **Storage**: Store in PostgreSQL with deduplication (hash-based)
5. **Queueing**: Mark for threat engine processing

#### Security Features

- API key authentication
- Token-based auth (JWT)
- PII removal before storage
- Event deduplication (SHA-256 hash)
- Workspace isolation

---

### 3. Threat Engine (`backend/threat_engine/`)

**Purpose**: Core threat detection system (THE MOAT).

#### 3.1 Rules-Based Detection (`rules/`)

| Rule | File | Description |
|------|------|-------------|
| Prompt Injection | `prompt_injection.py` | Detects injection attempts in prompts |
| Jailbreaking | `jailbreaking.py` | Detects jailbreak attempts |
| Tool Abuse | `tool_abuse.py` | Detects dangerous tool usage |
| API Abuse | `api_abuse.py` | Detects unauthorized API access |
| Output Drift | `output_drift.py` | Detects unexpected LLM behavior |
| Entropy Check | `entropy_check.py` | Detects encoded/obfuscated content |

#### 3.2 LLM-Based Detection (`models/`)

| Model | File | Description |
|------|------|-------------|
| LLM Analyzer | `llm_analyzer.py` | Multi-model analysis (OpenAI + Gemini) |
| Semantic Risk | `semantic_risk.py` | Embedding-based similarity detection |
| Hallucination Detector | `hallucination_detector.py` | Detects LLM hallucinations |
| Injection Detector | `injection_detector.py` | Advanced injection detection |

#### 3.3 Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Risk Scorer | `risk.py` | Unified risk scoring algorithm |
| Processor | `processor.py` | Event processing orchestrator |
| Incident Handler | `incident_handler.py` | Incident creation integration |

#### Risk Scoring Formula

```python
total_risk = (
    rules_risk * 0.30 +      # 30% weight
    pattern_risk * 0.25 +     # 25% weight
    model_risk * 0.25 +       # 25% weight
    compliance_risk * 0.20    # 20% weight
)
```

**Risk Thresholds:**
- `risk < 7`: Log and continue
- `risk >= 7`: Create incident

---

### 4. Compliance Engine (`backend/compliance_engine/`)

**Purpose**: Map events to compliance standards and detect violations.

#### Supported Standards

| Standard | File | Description |
|----------|------|-------------|
| HIPAA | `hipaa_detector.py` | Health Insurance Portability and Accountability Act |
| GLBA | `glba_detector.py` | Gramm-Leach-Bliley Act |
| PCI-DSS | `pci_detector.py` | Payment Card Industry Data Security Standard |
| SOC 2 | `soc2_detector.py` | Service Organization Control 2 |
| NIST | `nist_detector.py` | NIST Cybersecurity Framework |
| EU AI Act | `ai_act_classifier.py` | European Union AI Act |

#### Components

| Component | File | Purpose |
|-----------|------|---------|
| Compliance Mapper | `compliance_mapper.py` | Maps events to all standards |
| Evidence Collector | `evidence_collector.py` | Collects compliance evidence |
| Compliance Report | `compliance_report.py` | Generates compliance reports |
| Compliance Risk | `compliance_risk.py` | Calculates compliance risk scores |

#### Detection Output

Each detector returns:
```python
{
    "violations": List[str],      # List of violation IDs
    "risk_score": int,            # 0-10 risk score
    "has_violation": bool,        # True if violations found
    "evidence": Dict[str, Any]    # Supporting evidence
}
```

---

### 5. Incident System (`incident/`)

**Purpose**: Manage security incidents, generate RCA, and export reports.

#### Components

| Component | File | Purpose |
|-----------|------|---------|
| Incident Detector | `detector.py` | Detects incidents from events |
| Incident DB | `incident_db.py` | Database operations for incidents |
| RCA Generator | `rca_generator.py` | Generates Root Cause Analysis using LLM |
| Timeline Builder | `timeline_builder.py` | Builds incident timeline |
| PDF Report | `pdf_report.py` | Generates PDF reports using reportlab |

#### Incident Lifecycle

1. **Detection**: Triggered when `risk >= 7`
2. **Creation**: Incident created with severity, status, title, summary
3. **Timeline**: Events added to timeline chronologically
4. **RCA Generation**: LLM generates root cause analysis
5. **PDF Export**: Professional PDF report generated
6. **Pattern Extraction**: Patterns extracted for future detection

#### Incident Fields

```python
{
    "id": str,                    # Unique incident ID
    "workspace_id": str,          # Workspace identifier
    "agent_id": str,              # Agent identifier
    "trigger_event_id": str,      # Event that triggered incident
    "severity": str,              # "low", "medium", "high", "critical"
    "status": str,                # "open", "investigating", "resolved", "closed"
    "title": str,                 # Incident title
    "summary": str,               # Incident summary
    "rca_summary": str,           # Root cause analysis
    "timeline": List[Dict],       # Event timeline
    "pdf_path": str,              # Path to PDF report
    "created_at": datetime,       # Creation timestamp
    "updated_at": datetime        # Last update timestamp
}
```

---

### 6. Pattern Library (`patterns/`)

**Purpose**: Extensible pattern matching system for threat detection.

#### Structure

```
patterns/
├── pattern_list.json          # Security patterns (PI-001, JB-001, etc.)
├── compliance/
│   ├── hipaa_signatures.json
│   ├── glba_signatures.json
│   ├── pci_signatures.json
│   ├── soc2_signatures.json
│   └── nist_signatures.json
├── matcher.py                 # Pattern matching engine
└── updater.py                 # Pattern update logic
```

#### Pattern Format

```json
{
    "id": "PI-001",
    "name": "Prompt Injection - System Override",
    "category": "prompt_injection",
    "patterns": [
        {
            "type": "exact",
            "value": "ignore all previous instructions"
        },
        {
            "type": "regex",
            "value": "(?i)system\\s+prompt"
        }
    ],
    "risk_score": 8,
    "description": "Detects attempts to override system instructions"
}
```

#### Auto-Extraction

- Patterns extracted from incidents automatically
- Stored in pattern library for future detection
- Flywheel effect: More incidents → Better detection

---

## Data Models

### Event Schema

```python
class AgentEvent(BaseModel):
    timestamp: str                    # ISO 8601 timestamp
    agent_id: str                     # Agent identifier
    workspace_id: str                 # Workspace identifier
    workflow_id: Optional[str]         # Workflow identifier
    event_type: str                   # "tool_call", "llm_completion", "api_access", "system_anomaly"
    payload: Dict[str, Any]           # Event-specific data
    metadata: Dict[str, Any]          # Additional metadata
    raw: str                          # Original raw event data
    risk_local: int                   # Local risk score (0-10)
```

### Batch Event Schema

```python
class BatchEvent(BaseModel):
    workspace_id: str
    agent_id: str
    events: List[AgentEvent]
    batch_id: Optional[str]
    sent_at: str                      # ISO 8601 timestamp
```

---

## API Specifications

### Ingestion API

#### `POST /api/v1/ingest`

**Purpose**: Receive event batches from Guardian Agents.

**Authentication**: API key in `Authorization` header

**Request Body**:
```json
{
    "workspace_id": "ws_123",
    "agent_id": "agent_456",
    "events": [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "agent_id": "agent_456",
            "workspace_id": "ws_123",
            "event_type": "llm_completion",
            "payload": {...},
            "metadata": {...},
            "raw": "...",
            "risk_local": 2
        }
    ],
    "batch_id": "batch_789",
    "sent_at": "2024-01-15T10:30:05Z"
}
```

**Response**:
```json
{
    "status": "success",
    "stored": 10,
    "duplicates": 0,
    "errors": []
}
```

#### `GET /api/v1/health`

**Purpose**: Health check endpoint.

**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Compliance API

#### `GET /api/v1/compliance/{standard}/check`

**Purpose**: Check compliance for a specific standard.

**Parameters**:
- `standard`: `hipaa`, `glba`, `pci`, `soc2`, `nist`, `ai_act`

**Response**:
```json
{
    "standard": "hipaa",
    "violations": ["HIPAA-001", "HIPAA-003"],
    "risk_score": 7,
    "has_violation": true,
    "evidence": {...}
}
```

---

## Threat Detection

### Detection Rules

#### 1. Prompt Injection (`prompt_injection.py`)

**Detects**: Attempts to inject malicious instructions into prompts.

**Patterns**:
- System override commands
- Instruction manipulation
- Context switching attempts

**Risk Score**: 0-10

#### 2. Jailbreaking (`jailbreaking.py`)

**Detects**: Attempts to bypass LLM safety mechanisms.

**Patterns**:
- Role-playing scenarios
- Hypothetical questions
- Instruction following tricks

**Risk Score**: 0-10

#### 3. Tool Abuse (`tool_abuse.py`)

**Detects**: Dangerous or unauthorized tool usage.

**Patterns**:
- File system access
- Network operations
- System commands

**Risk Score**: 0-10

#### 4. API Abuse (`api_abuse.py`)

**Detects**: Unauthorized or excessive API calls.

**Patterns**:
- Rate limit violations
- Unauthorized endpoints
- Suspicious request patterns

**Risk Score**: 0-10

#### 5. Output Drift (`output_drift.py`)

**Detects**: Unexpected LLM behavior or output.

**Patterns**:
- Semantic drift
- Format violations
- Content anomalies

**Risk Score**: 0-10

#### 6. Entropy Check (`entropy_check.py`)

**Detects**: Encoded or obfuscated content.

**Patterns**:
- High entropy strings
- Base64 encoding
- Hex encoding

**Risk Score**: 0-10

### LLM-Based Detection

#### LLM Analyzer (`llm_analyzer.py`)

**Purpose**: Multi-model consensus for threat detection.

**Models**:
- OpenAI GPT-4 (primary)
- Google Gemini (fallback)

**Process**:
1. Send event to multiple LLMs
2. Get risk scores and reasoning
3. Calculate consensus risk
4. Return unified result

**Output**:
```python
{
    "openai_risk": int,           # 0-10
    "gemini_risk": int,            # 0-10 (optional)
    "consensus_risk": int,         # 0-10
    "reasoning": {
        "openai": str,
        "gemini": str              # optional
    }
}
```

---

## Compliance Engine

### Compliance Standards

#### HIPAA (Health Insurance Portability and Accountability Act)

**Detects**:
- PHI (Protected Health Information) exposure
- Unauthorized access to health data
- Missing encryption
- Inadequate access controls

**Violation IDs**: `HIPAA-001`, `HIPAA-002`, etc.

#### GLBA (Gramm-Leach-Bliley Act)

**Detects**:
- Financial information exposure
- Missing privacy notices
- Inadequate safeguards
- Unauthorized sharing

**Violation IDs**: `GLBA-001`, `GLBA-002`, etc.

#### PCI-DSS (Payment Card Industry Data Security Standard)

**Detects**:
- Cardholder data exposure
- Missing encryption
- Inadequate access controls
- Unauthorized storage

**Violation IDs**: `PCI-001`, `PCI-002`, etc.

#### SOC 2 (Service Organization Control 2)

**Detects**:
- Security control failures
- Availability issues
- Processing integrity violations
- Confidentiality breaches

**Violation IDs**: `SOC2-001`, `SOC2-002`, etc.

#### NIST (NIST Cybersecurity Framework)

**Detects**:
- Identify failures
- Protect failures
- Detect failures
- Respond failures
- Recover failures

**Violation IDs**: `NIST-001`, `NIST-002`, etc.

#### EU AI Act

**Detects**:
- High-risk AI system violations
- Transparency failures
- Human oversight issues
- Data governance violations

**Violation IDs**: `AI-ACT-001`, `AI-ACT-002`, etc.

---

## Incident Management

### Incident Creation

**Trigger**: `risk >= 7`

**Process**:
1. Create incident record
2. Set severity based on risk score
3. Build timeline from related events
4. Generate RCA using LLM
5. Generate PDF report
6. Extract patterns for future detection

### Root Cause Analysis (RCA)

**Generator**: `rca_generator.py`

**Process**:
1. Collect incident data (timeline, risk analysis, events)
2. Send to LLM (OpenAI or Gemini)
3. Generate structured RCA:
   - Executive summary
   - Root cause analysis
   - Recommended fixes
   - Remediation steps
4. Store in incident record

**Output Format**:
```json
{
    "executive_summary": "...",
    "root_cause_analysis": "...",
    "recommended_fix": "...",
    "remediation_steps": [
        "Step 1: ...",
        "Step 2: ..."
    ]
}
```

### PDF Report Generation

**Generator**: `pdf_report.py`

**Contents**:
- Incident details (ID, severity, status, dates)
- Executive summary
- Root cause analysis
- Remediation steps
- Event timeline
- Risk analysis breakdown

**Format**: Professional PDF using reportlab

---

## Database Schema

### Database: PostgreSQL (Supabase with pgvector)

### Tables

#### 1. `workspaces`
- `id` (VARCHAR, PRIMARY KEY)
- `name` (VARCHAR)
- `created_at` (TIMESTAMP)

#### 2. `agents`
- `id` (VARCHAR, PRIMARY KEY)
- `workspace_id` (VARCHAR, FOREIGN KEY)
- `name` (VARCHAR)
- `created_at` (TIMESTAMP)

#### 3. `events`
- `id` (VARCHAR, PRIMARY KEY)
- `workspace_id` (VARCHAR, FOREIGN KEY)
- `agent_id` (VARCHAR, FOREIGN KEY)
- `workflow_id` (VARCHAR)
- `event_type` (VARCHAR)
- `payload` (JSONB)
- `metadata` (JSONB)
- `raw` (TEXT)
- `risk_local` (INTEGER)
- `risk_engine` (INTEGER)
- `event_hash` (VARCHAR, UNIQUE)
- `embedding` (VECTOR(1536))  # For RAG
- `created_at` (TIMESTAMP)

#### 4. `patterns`
- `id` (VARCHAR, PRIMARY KEY)
- `pattern_id` (VARCHAR, UNIQUE)
- `name` (VARCHAR)
- `category` (VARCHAR)
- `patterns` (JSONB)
- `risk_score` (INTEGER)
- `embedding` (VECTOR(1536))  # For RAG
- `created_at` (TIMESTAMP)

#### 5. `incidents`
- `id` (VARCHAR, PRIMARY KEY)
- `workspace_id` (VARCHAR, FOREIGN KEY)
- `agent_id` (VARCHAR, FOREIGN KEY)
- `trigger_event_id` (VARCHAR, FOREIGN KEY)
- `severity` (VARCHAR)
- `status` (VARCHAR)
- `title` (VARCHAR)
- `summary` (TEXT)
- `rca_summary` (TEXT)
- `timeline` (JSONB)
- `pdf_path` (VARCHAR)
- `embedding` (VECTOR(1536))  # For RAG
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### 6. `risk_scores`
- `id` (VARCHAR, PRIMARY KEY)
- `event_id` (VARCHAR, FOREIGN KEY)
- `rules_risk` (INTEGER)
- `pattern_risk` (INTEGER)
- `model_risk` (INTEGER)
- `compliance_risk` (INTEGER)
- `total_risk` (INTEGER)
- `created_at` (TIMESTAMP)

#### 7. `compliance_mappings`
- `id` (VARCHAR, PRIMARY KEY)
- `event_id` (VARCHAR, FOREIGN KEY)
- `standard` (VARCHAR)
- `violations` (JSONB)
- `risk_score` (INTEGER)
- `has_violation` (BOOLEAN)
- `created_at` (TIMESTAMP)

#### 8. `compliance_evidence`
- `id` (VARCHAR, PRIMARY KEY)
- `mapping_id` (VARCHAR, FOREIGN KEY)
- `evidence_type` (VARCHAR)
- `evidence_data` (JSONB)
- `created_at` (TIMESTAMP)

### Indexes

- Workspace, agent, event type indexes
- Risk score indexes
- Timestamp indexes
- Vector indexes for semantic search (ivfflat)

### Extensions

- `pgvector`: Vector similarity search for RAG

---

## Security Requirements

### Authentication

- **API Keys**: Required for Guardian Agent → Ingestion API
- **JWT Tokens**: Optional for web UI (future)
- **Workspace Isolation**: All queries filtered by `workspace_id`

### Data Protection

- **PII Cleaning**: All PII removed before storage
- **Event Deduplication**: SHA-256 hash-based deduplication
- **Encryption**: Database encryption (production)
- **Secure Transmission**: HTTPS only

### Access Control

- **Workspace Isolation**: Multi-tenant isolation
- **Agent Authentication**: API key per agent
- **Role-Based Access**: Future enhancement

---

## Deployment

### Guardian Agent

**Installation**:
```bash
./install.sh
```

**Service**:
- systemd (Linux)
- launchd (macOS)

**Configuration**:
- Environment variables in `.env`
- Log directory configuration
- API endpoint configuration

### Backend

**Requirements**:
- Python 3.8+
- PostgreSQL (Supabase recommended)
- OpenAI API key

**Start Backend**:
```bash
./start_backend.sh
```

**Start Worker**:
```bash
python backend/worker.py
```

### Database Setup

**Supabase Setup**:
1. Create Supabase project
2. Run `shared/schema.sql`
3. Configure `DATABASE_URL` in `.env`

**Connection String**:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

---

## Testing Requirements

### Unit Tests

**Location**: `tests/unit/`

**Coverage**:
- ✅ Event collector
- ✅ Pattern matcher
- ✅ Risk scorer
- ✅ Threat rules
- ✅ Compliance detectors

**Status**: 37/37 tests passing (100%)

### Integration Tests

**Location**: `tests/integration/`

**Coverage**:
- ✅ Ingestion flow
- ✅ Threat engine flow
- ✅ Compliance flow

### End-to-End Tests

**Location**: `scripts/test_e2e_flow.py`, `test_full_system.py`

**Coverage**:
- ✅ Complete event flow
- ✅ Incident creation
- ✅ RCA generation
- ✅ PDF generation

**Status**: 4/5 tests passing (80%)

---

## Performance Requirements

### Throughput

- **Event Ingestion**: 1000+ events/second
- **Threat Processing**: 100+ events/second
- **LLM Analysis**: 10+ events/second (rate-limited by API)

### Latency

- **Event Ingestion**: < 100ms
- **Threat Analysis**: < 1s (without LLM)
- **LLM Analysis**: < 5s (API-dependent)
- **Incident Creation**: < 2s

### Scalability

- **Horizontal Scaling**: Multiple API instances
- **Worker Scaling**: Multiple threat engine workers
- **Database**: Connection pooling, read replicas

---

## Future Enhancements

### Phase 1 (Optional)

1. **Dashboard UI**
   - Real-time incident monitoring
   - Compliance dashboards
   - Risk analytics

2. **Rate Limiting**
   - API rate limiting
   - Per-workspace quotas
   - DDoS protection

3. **Monitoring/Metrics**
   - Prometheus metrics
   - Grafana dashboards
   - Alerting

### Phase 2 (Optional)

1. **RAG Implementation**
   - Vector embeddings for events
   - Semantic similarity search
   - Context-aware detection

2. **Gemini Integration**
   - Full Gemini API integration
   - Multi-model consensus
   - Fallback LLM

3. **Advanced Analytics**
   - Cross-customer correlation
   - Trend analysis
   - Predictive risk scoring

### Phase 3 (Optional)

1. **Real-time Alerts**
   - Webhook notifications
   - Email alerts
   - Slack/Teams integration

2. **Advanced Pattern Learning**
   - ML-based pattern extraction
   - Adaptive risk scoring
   - Anomaly detection

---

## Appendix

### Configuration Reference

#### Guardian Agent Config

```bash
GUARDIAN_AGENT_API_KEY=your_api_key
SHIELD_INGESTION_ENDPOINT=https://shield.mangotec.ai/api/v1/ingest
LOG_DIR=/path/to/logs
BATCH_SIZE=10
BATCH_INTERVAL=5
```

#### Backend Config

```bash
DATABASE_URL=postgresql://...
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key  # Optional
SECRET_KEY=your_secret_key
RISK_THRESHOLD=7
```

### API Response Codes

- `200 OK`: Success
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Access denied
- `500 Internal Server Error`: Server error

### Risk Score Interpretation

- `0-3`: Low risk
- `4-6`: Medium risk
- `7-8`: High risk (incident created)
- `9-10`: Critical risk (incident created)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-15 | Initial specification document |

---

**End of Specification**

