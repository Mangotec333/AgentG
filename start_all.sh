#!/bin/bash
# Start both backend and Streamlit UI

cd "$(dirname "$0")"

echo "🧪 Starting AgentG Test Runner..."
echo ""

# Kill any existing processes
pkill -f "router.py" 2>/dev/null
pkill -f "streamlit" 2>/dev/null
sleep 1

# Start backend
echo "1️⃣ Starting backend..."
cd backend/ingestion
python3 router.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..
sleep 3

# Check backend
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend running (PID: $BACKEND_PID)"
else
    echo "   ⚠️  Backend may have issues. Check /tmp/backend.log"
fi

# Start Streamlit
echo ""
echo "2️⃣ Starting Streamlit UI..."
echo "   Open: http://localhost:8501"
echo ""
python3 -m streamlit run test_runner_ui.py --server.port 8501

