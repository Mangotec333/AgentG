-- AI Workflow Shield Database Schema
-- PostgreSQL schema for storing events, patterns, incidents, and risk scores

-- Workspaces
CREATE TABLE IF NOT EXISTS workspaces (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agents
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255),
    version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP,
    INDEX idx_agents_workspace (workspace_id)
);

-- Events (raw telemetry)
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    workflow_id VARCHAR(255),
    event_type VARCHAR(50) NOT NULL,
    payload JSONB,
    metadata JSONB,
    raw TEXT,
    risk_local INTEGER DEFAULT 0,
    risk_engine INTEGER,
    event_hash VARCHAR(64) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_events_workspace (workspace_id),
    INDEX idx_events_agent (agent_id),
    INDEX idx_events_type (event_type),
    INDEX idx_events_created (created_at),
    INDEX idx_events_risk (risk_engine)
);

-- Threat Patterns (proprietary signature library)
CREATE TABLE IF NOT EXISTS patterns (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    signature TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    match_count INTEGER DEFAULT 0,
    INDEX idx_patterns_category (category),
    INDEX idx_patterns_severity (severity)
);

-- Pattern Matches (track which patterns matched which events)
CREATE TABLE IF NOT EXISTS pattern_matches (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    pattern_id VARCHAR(50) NOT NULL REFERENCES patterns(id) ON DELETE CASCADE,
    matched_text TEXT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_matches_event (event_id),
    INDEX idx_matches_pattern (pattern_id)
);

-- Risk Scores (computed risk assessments)
CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    rules_risk INTEGER DEFAULT 0,
    model_risk INTEGER DEFAULT 0,
    pattern_risk INTEGER DEFAULT 0,
    compliance_risk INTEGER DEFAULT 0,
    total_risk INTEGER NOT NULL,
    model_details JSONB,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_risk_event (event_id),
    INDEX idx_risk_total (total_risk)
);

-- Incidents (triggered security events)
CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    trigger_event_id VARCHAR(255) NOT NULL REFERENCES events(id) ON DELETE SET NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    title VARCHAR(255),
    summary TEXT,
    rca_summary TEXT,
    timeline JSONB,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    INDEX idx_incidents_workspace (workspace_id),
    INDEX idx_incidents_status (status),
    INDEX idx_incidents_severity (severity),
    INDEX idx_incidents_created (created_at)
);

-- Incident Events (events associated with an incident)
CREATE TABLE IF NOT EXISTS incident_events (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    event_id VARCHAR(255) NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(incident_id, event_id),
    INDEX idx_incident_events_incident (incident_id),
    INDEX idx_incident_events_event (event_id)
);

-- Compliance Mappings (compliance flags per event)
CREATE TABLE IF NOT EXISTS compliance_mappings (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    hipaa_violations JSONB,
    glba_violations JSONB,
    pci_violations JSONB,
    soc2_violations JSONB,
    nist_violations JSONB,
    ai_act_category VARCHAR(50),
    compliance_risk INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_compliance_event (event_id),
    INDEX idx_compliance_risk (compliance_risk)
);

-- Compliance Evidence (links incidents to evidence)
CREATE TABLE IF NOT EXISTS compliance_evidence (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    evidence_path VARCHAR(500),
    evidence_type VARCHAR(50),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_evidence_incident (incident_id)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_events_workflow ON events(workflow_id) WHERE workflow_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_risk_range ON events(risk_engine) WHERE risk_engine >= 7;

