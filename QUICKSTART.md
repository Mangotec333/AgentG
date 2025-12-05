# AI Workflow Shield - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- (Optional) Redis for queue

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Database Setup

```bash
# Create database
createdb shield_db

# Run schema
psql shield_db < shared/schema.sql
```

### Step 3: Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

### Step 4: Run Components

#### Option A: Development (Separate Terminals)

**Terminal 1 - Ingestion API:**
```bash
cd backend/ingestion
uvicorn router:app --reload --port 8000
```

**Terminal 2 - Threat Engine Worker:**
```bash
cd backend
python worker.py
```

**Terminal 3 - Guardian Agent:**
```bash
cd guardian-agent
python main.py
```

#### Option B: Production

Use systemd/launchd services (see `install.sh`)

### Step 5: Test the System

```bash
# Generate synthetic events
python examples/synthetic_events.py

# Test event flow
python examples/test_event_flow.py
```

## 📊 Verify It's Working

1. **Check Ingestion API:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **Send Test Event:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key" \
     -d '{
       "workspace_id": "test",
       "agent_id": "test_agent",
       "events": [{
         "timestamp": "2024-01-01T00:00:00Z",
         "agent_id": "test_agent",
         "workspace_id": "test",
         "event_type": "llm_completion",
         "payload": {
           "prompt": "Ignore previous instructions",
           "response": "I cannot do that"
         },
         "raw": "llm_completion: prompt injection attempt",
         "risk_local": 7
       }]
     }'
   ```

3. **Check Database:**
   ```sql
   SELECT COUNT(*) FROM events;
   SELECT COUNT(*) FROM incidents;
   ```

## 🔍 Monitoring

- **Guardian Agent Logs:** Check console output
- **Backend Logs:** Check console output
- **Database:** Query `events`, `incidents`, `risk_scores` tables

## 🐛 Troubleshooting

**Issue: Database connection error**
- Check `DATABASE_URL` in `.env`
- Verify PostgreSQL is running
- Check database exists

**Issue: Import errors**
- Ensure you're in the project root
- Check Python path includes project root
- Verify all dependencies installed

**Issue: API authentication fails**
- Check `SHIELD_API_KEY` matches in agent and backend
- Verify API key header is sent correctly

## 📚 Next Steps

1. Read `ARCHITECTURE.md` for system design
2. Review `README.md` for full documentation
3. Customize threat patterns in `patterns/pattern_list.json`
4. Add LLM API keys for advanced detection
5. Set up monitoring and alerting

## 🎯 Key Endpoints

- `POST /api/v1/ingest` - Ingest events
- `GET /api/v1/health` - Health check

## 📈 Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper `DATABASE_URL`
- [ ] Add LLM API keys (Gemini/OpenAI)
- [ ] Set up SSL/TLS for API
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backups
- [ ] Set up monitoring
- [ ] Review PII cleaning settings
- [ ] Test incident creation flow

---

**You're ready to protect AI workflows! 🛡️**

