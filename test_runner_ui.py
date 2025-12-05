"""
Streamlit UI for AgentG Test Runner.
Run tests and view results in a friendly interface.
"""
import streamlit as st
import requests
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_RUN_ENDPOINT = f"{API_BASE_URL}/api/v1/tests/run"
TEST_STATUS_ENDPOINT = f"{API_BASE_URL}/api/v1/tests/status"
TEST_RESULTS_ENDPOINT = f"{API_BASE_URL}/api/v1/tests/results"
TEST_LIST_ENDPOINT = f"{API_BASE_URL}/api/v1/tests/list"

# Page config
st.set_page_config(
    page_title="AgentG Test Runner",
    page_icon="🧪",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .test-passed {
        color: #00cc00;
        font-weight: bold;
    }
    .test-failed {
        color: #ff0000;
        font-weight: bold;
    }
    .test-running {
        color: #ffaa00;
        font-weight: bold;
    }
    .summary-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def check_api_connection() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def run_tests(test_type: str) -> Optional[str]:
    """Start a test run and return test_run_id."""
    try:
        response = requests.post(
            f"{TEST_RUN_ENDPOINT}?test_type={test_type}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("test_run_id")
        else:
            st.error(f"Error starting tests: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running:")
        st.code("cd backend/ingestion && python router.py")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_test_status(test_run_id: str) -> Optional[Dict[str, Any]]:
    """Get current status of a test run."""
    try:
        response = requests.get(f"{TEST_STATUS_ENDPOINT}/{test_run_id}", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_test_results(test_run_id: str) -> Optional[Dict[str, Any]]:
    """Get results of a completed test run."""
    try:
        response = requests.get(f"{TEST_RESULTS_ENDPOINT}/{test_run_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def poll_test_results(test_run_id: str, progress_bar, status_text):
    """Poll for test results until complete."""
    max_wait_time = 300  # 5 minutes max
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait_time:
        status = get_test_status(test_run_id)
        
        if not status:
            status_text.error("❌ Could not get test status")
            return None
        
        current_status = status.get("status", "unknown")
        
        # Update progress
        if current_status == "running":
            progress = status.get("progress", 0)
            progress_bar.progress(progress / 100)
            status_text.info(f"⏳ Running tests... ({progress}%)")
        elif current_status in ["completed", "failed", "error"]:
            progress_bar.progress(100)
            results = get_test_results(test_run_id)
            return results
        else:
            status_text.warning(f"Status: {current_status}")
        
        # Check if status changed
        if current_status != last_status:
            last_status = current_status
            if current_status == "running":
                status_text.info("⏳ Tests are running...")
        
        time.sleep(1)  # Poll every second
    
    status_text.error("⏱️ Test run timed out")
    return None


def display_test_results(results: Dict[str, Any]):
    """Display test results in a nice format."""
    if not results:
        st.error("No results to display")
        return
    
    summary = results.get("summary", {})
    tests = results.get("tests", [])
    status = results.get("status", "unknown")
    
    # Summary box
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tests", summary.get("total", 0))
    
    with col2:
        st.metric("✅ Passed", summary.get("passed", 0), delta=None)
    
    with col3:
        st.metric("❌ Failed", summary.get("failed", 0), delta=None)
    
    with col4:
        duration = summary.get("duration", 0)
        st.metric("Duration", f"{duration:.2f}s")
    
    # Status badge
    if status == "completed" and summary.get("failed", 0) == 0:
        st.success("✅ All tests passed!")
    elif status == "completed":
        st.warning(f"⚠️ {summary.get('failed', 0)} test(s) failed")
    elif status == "failed":
        st.error("❌ Test run failed")
    else:
        st.info(f"Status: {status}")
    
    st.divider()
    
    # Test results
    st.subheader("Test Results")
    
    if not tests:
        st.info("No test results available")
        return
    
    # Group by status
    passed_tests = [t for t in tests if t.get("status") == "passed"]
    failed_tests = [t for t in tests if t.get("status") == "failed"]
    
    # Display failed tests first (more important)
    if failed_tests:
        st.subheader("❌ Failed Tests", divider="red")
        for test in failed_tests:
            with st.expander(f"❌ {test.get('name', 'Unknown')} ({test.get('duration', 0):.2f}s)", expanded=True):
                error = test.get("error", "No error message")
                st.code(error, language="text")
    
    # Display passed tests
    if passed_tests:
        st.subheader("✅ Passed Tests", divider="green")
        # Show in columns for better layout
        cols = st.columns(3)
        for i, test in enumerate(passed_tests):
            with cols[i % 3]:
                duration = test.get("duration", 0)
                st.success(f"✅ {test.get('name', 'Unknown')} ({duration:.2f}s)")
    
    # Show stdout/stderr if available
    stdout = results.get("stdout", "")
    stderr = results.get("stderr", "")
    
    if stdout or stderr:
        st.divider()
        st.subheader("Output")
        
        if stdout:
            with st.expander("📄 Standard Output"):
                st.code(stdout, language="text")
        
        if stderr:
            with st.expander("⚠️ Standard Error"):
                st.code(stderr, language="text")


def main():
    """Main Streamlit app."""
    # Header
    st.title("🧪 AgentG Test Runner")
    st.markdown("Run tests and view results for AI Workflow Shield")
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to API. Please start the backend:")
        st.code("cd backend/ingestion && python router.py")
        st.info("Or: `uvicorn backend.ingestion.router:app --host 0.0.0.0 --port 8000`")
        return
    
    st.success("✅ Connected to API")
    
    # Sidebar for test selection
    with st.sidebar:
        st.header("Test Suites")
        st.markdown("Select which tests to run:")
        
        test_type = st.radio(
            "Test Type",
            ["unit", "integration", "e2e", "all"],
            help="Unit: Individual components\nIntegration: Component interactions\nE2E: End-to-end flows\nAll: Run everything"
        )
        
        st.divider()
        
        st.markdown("### Recent Test Runs")
        try:
            response = requests.get(TEST_LIST_ENDPOINT, params={"limit": 5}, timeout=2)
            if response.status_code == 200:
                runs = response.json()
                for run in runs:
                    status = run.get("status", "unknown")
                    test_type_run = run.get("test_type", "unknown")
                    started = run.get("started_at", "")[:19] if run.get("started_at") else "Unknown"
                    
                    if status == "completed":
                        st.success(f"✅ {test_type_run} - {started}")
                    elif status == "failed":
                        st.error(f"❌ {test_type_run} - {started}")
                    elif status == "running":
                        st.warning(f"⏳ {test_type_run} - {started}")
                    else:
                        st.info(f"ℹ️ {test_type_run} - {started}")
        except:
            st.info("No recent test runs")
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(f"▶️ Run {test_type.upper()} Tests", type="primary", use_container_width=True):
            # Initialize session state
            if "test_run_id" not in st.session_state:
                st.session_state.test_run_id = None
            if "test_results" not in st.session_state:
                st.session_state.test_results = None
            
            # Start test run
            with st.spinner("Starting test run..."):
                test_run_id = run_tests(test_type)
            
            if test_run_id:
                st.session_state.test_run_id = test_run_id
                st.session_state.test_results = None
                
                # Create progress bar and status
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Poll for results
                results = poll_test_results(test_run_id, progress_bar, status_text)
                
                if results:
                    st.session_state.test_results = results
                    progress_bar.empty()
                    status_text.empty()
    
    # Display results if available
    if st.session_state.get("test_results"):
        st.divider()
        display_test_results(st.session_state.test_results)
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        1. **Select Test Type**: Choose unit, integration, e2e, or all tests
        2. **Click Run**: Press the "Run Tests" button
        3. **Wait**: Tests will run and progress will be shown
        4. **View Results**: See pass/fail status, errors, and output
        
        **Note**: Make sure the backend API is running on port 8000
        """)


if __name__ == "__main__":
    main()

