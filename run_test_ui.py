#!/usr/bin/env python3
"""
Single script to run both backend and Streamlit UI.
Run this in one terminal and both services will start.
"""
import subprocess
import sys
import os
import time
import signal
import requests
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.absolute()
os.chdir(PROJECT_ROOT)

# Store process IDs
backend_process = None
streamlit_process = None


def cleanup(signum=None, frame=None):
    """Cleanup function to stop both processes."""
    print("\n🛑 Stopping services...")
    
    if backend_process:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("   ✅ Backend stopped")
    
    if streamlit_process:
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
        print("   ✅ Streamlit stopped")
    
    print("✅ All services stopped")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print("🧪 Starting AgentG Test Runner...")
print("=" * 50)
print()

# Check dependencies
print("1️⃣ Checking dependencies...")
try:
    import streamlit
    print("   ✅ Streamlit installed")
except ImportError:
    print("   Installing streamlit...")
    subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "--quiet"], check=True)

try:
    import fastapi
    print("   ✅ FastAPI installed")
except ImportError:
    print("   Installing fastapi...")
    subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "--quiet"], check=True)

# Start backend
print()
print("2️⃣ Starting backend on port 8000...")
backend_dir = PROJECT_ROOT / "backend" / "ingestion"
backend_process = subprocess.Popen(
    [sys.executable, "router.py"],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for backend to start
print("   Waiting for backend to start...")
for i in range(10):
    time.sleep(0.5)
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=1)
        if response.status_code == 200:
            print(f"   ✅ Backend is running (PID: {backend_process.pid})")
            break
    except:
        pass
else:
    print("   ⚠️  Backend may not have started properly")
    print("   Continuing anyway...")

# Start Streamlit
print()
print("3️⃣ Starting Streamlit UI on port 8501...")
print("   Browser will open automatically")
print()
print("   Press Ctrl+C to stop both services")
print("   " + "=" * 50)
print()

streamlit_process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "test_runner_ui.py", "--server.port", "8501"],
    cwd=PROJECT_ROOT
)

# Wait for streamlit to finish (or be interrupted)
try:
    streamlit_process.wait()
except KeyboardInterrupt:
    pass

# Cleanup
cleanup()

