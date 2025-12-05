#!/bin/bash

# Test Runner UI Startup Script

echo "🧪 AgentG Test Runner - Setup & Test"
echo "====================================="
echo ""

# Check if backend is running
echo "1️⃣ Checking if backend is running..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8000"
    BACKEND_RUNNING=true
else
    echo "   ⚠️  Backend is not running"
    BACKEND_RUNNING=false
fi

# Check if streamlit is installed
echo ""
echo "2️⃣ Checking dependencies..."
if python3 -c "import streamlit" 2>/dev/null; then
    echo "   ✅ Streamlit is installed"
else
    echo "   ❌ Streamlit not installed. Installing..."
    pip3 install streamlit --quiet
    echo "   ✅ Streamlit installed"
fi

if python3 -c "import requests" 2>/dev/null; then
    echo "   ✅ Requests is installed"
else
    echo "   ❌ Requests not installed. Installing..."
    pip3 install requests --quiet
    echo "   ✅ Requests installed"
fi

# Start backend if not running
if [ "$BACKEND_RUNNING" = false ]; then
    echo ""
    echo "3️⃣ Starting backend..."
    echo "   Starting FastAPI server on port 8000..."
    cd backend/ingestion
    python3 router.py &
    BACKEND_PID=$!
    cd ../..
    
    # Wait for backend to start
    echo "   Waiting for backend to start..."
    sleep 3
    
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "   ✅ Backend started (PID: $BACKEND_PID)"
    else
        echo "   ❌ Backend failed to start"
        exit 1
    fi
else
    echo ""
    echo "3️⃣ Backend already running, skipping..."
fi

# Start Streamlit
echo ""
echo "4️⃣ Starting Streamlit UI..."
echo "   Opening browser at http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop both services"
echo ""

# Start streamlit
streamlit run test_runner_ui.py --server.port 8501

