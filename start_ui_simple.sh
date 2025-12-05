#!/bin/bash
# Simple script to start Streamlit UI

cd "$(dirname "$0")"

echo "🧪 Starting Streamlit Test Runner UI..."
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing streamlit..."
    pip3 install streamlit --quiet
fi

echo "Starting UI on http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

# Start streamlit
python3 -m streamlit run test_runner_ui.py --server.port 8501
