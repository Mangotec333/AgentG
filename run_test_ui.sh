#!/bin/bash

# Single script to run both backend and Streamlit UI in one terminal

echo "🧪 Starting AgentG Test Runner..."
echo "================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo "✅ Stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Check dependencies
echo "1️⃣ Checking dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "   Installing streamlit..."
    pip3 install streamlit --quiet
fi

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "   Installing fastapi..."
    pip3 install fastapi uvicorn --quiet
fi

# Start backend
echo ""
echo "2️⃣ Starting backend on port 8000..."
cd backend/ingestion
python3 router.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
echo "   Waiting for backend to start..."
sleep 3

# Check if backend started
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running (PID: $BACKEND_PID)"
else
    echo "   ⚠️  Backend may not have started. Check /tmp/backend.log"
    echo "   Continuing anyway..."
fi

# Start Streamlit
echo ""
echo "3️⃣ Starting Streamlit UI on port 8501..."
echo "   Browser will open automatically"
echo ""
echo "   Press Ctrl+C to stop both services"
echo "   ==================================="
echo ""

# Start streamlit in foreground
streamlit run test_runner_ui.py --server.port 8501

# Cleanup when streamlit exits
cleanup

