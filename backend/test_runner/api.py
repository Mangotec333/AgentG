"""
Test runner API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List, Dict, Any
import subprocess
import json
import uuid
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import backend_logger

router = APIRouter(prefix="/api/v1/tests", tags=["tests"])

# Store test run status in memory (in production, use Redis or DB)
test_runs: Dict[str, Dict[str, Any]] = {}


def run_pytest(test_type: str, test_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run pytest tests and return results.
    
    Args:
        test_type: "unit", "integration", "e2e", or "all"
        test_names: Optional list of specific test names to run
    
    Returns:
        Test results dictionary
    """
    # Build pytest command
    base_cmd = ["python", "-m", "pytest", "-v", "--tb=short"]
    
    # Add JSON report
    results_file = f"/tmp/pytest_results_{uuid.uuid4().hex[:8]}.json"
    base_cmd.extend(["--json-report", f"--json-report-file={results_file}"])
    
    # Determine test path
    if test_type == "unit":
        test_path = "tests/unit/"
    elif test_type == "integration":
        test_path = "tests/integration/"
    elif test_type == "e2e":
        test_path = "tests/e2e/"
    elif test_type == "all":
        test_path = "tests/"
    else:
        raise ValueError(f"Invalid test_type: {test_type}")
    
    # Add specific test names if provided
    if test_names:
        base_cmd.extend([f"tests/{test_type}/{name}" for name in test_names])
    else:
        base_cmd.append(test_path)
    
    # Add coverage if pytest-cov is installed
    try:
        import pytest_cov
        base_cmd.extend(["--cov=.", "--cov-report=term-missing"])
    except ImportError:
        pass
    
    backend_logger.info(f"Running pytest: {' '.join(base_cmd)}")
    
    # Get project root directory (2 levels up from backend/test_runner)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
    try:
        # Run pytest from project root
        result = subprocess.run(
            base_cmd,
            cwd=project_root,  # Run from project root!
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Parse results
        results = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        # Try to read JSON report if it exists
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    json_results = json.load(f)
                    results["json_report"] = json_results
                    
                    # Extract summary
                    summary = json_results.get("summary", {})
                    results["summary"] = {
                        "total": summary.get("total", 0),
                        "passed": summary.get("passed", 0),
                        "failed": summary.get("failed", 0),
                        "skipped": summary.get("skipped", 0),
                        "duration": summary.get("duration", 0)
                    }
                    
                    # Extract test results
                    tests = json_results.get("tests", [])
                    results["tests"] = [
                        {
                            "name": test.get("nodeid", "").split("::")[-1],
                            "status": "passed" if test.get("outcome") == "passed" else ("skipped" if test.get("outcome") == "skipped" else "failed"),
                            "duration": test.get("call", {}).get("duration", 0) if test.get("call") else 0,
                            "error": test.get("call", {}).get("longrepr", "") if test.get("outcome") not in ["passed", "skipped"] else None
                        }
                        for test in tests
                    ]
            except Exception as e:
                backend_logger.warning(f"Could not parse JSON report: {e}")
        
        return results
        
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": "Test run timed out after 5 minutes",
            "passed": False,
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "passed": False,
            "error": str(e)
        }


@router.post("/run")
async def run_tests(
    test_type: str,
    test_names: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Run tests and return test run ID.
    
    Args:
        test_type: "unit", "integration", "e2e", or "all"
        test_names: Optional list of specific test names
    
    Returns:
        Test run ID and initial status
    """
    test_run_id = str(uuid.uuid4())
    
    # Initialize test run status
    test_runs[test_run_id] = {
        "test_run_id": test_run_id,
        "test_type": test_type,
        "status": "running",
        "progress": 0,
        "current_test": None,
        "started_at": datetime.now().isoformat(),
        "results": None
    }
    
    # Run tests in background
    def run_and_update():
        try:
            results = run_pytest(test_type, test_names)
            test_runs[test_run_id]["status"] = "completed" if results["passed"] else "failed"
            test_runs[test_run_id]["results"] = results
            test_runs[test_run_id]["completed_at"] = datetime.now().isoformat()
            test_runs[test_run_id]["progress"] = 100
        except Exception as e:
            test_runs[test_run_id]["status"] = "error"
            test_runs[test_run_id]["error"] = str(e)
            test_runs[test_run_id]["completed_at"] = datetime.now().isoformat()
    
    # Run in background
    if background_tasks:
        background_tasks.add_task(run_and_update)
    else:
        # For testing, run synchronously
        run_and_update()
    
    return {
        "test_run_id": test_run_id,
        "status": "running",
        "test_type": test_type
    }


@router.get("/status/{test_run_id}")
async def get_test_status(test_run_id: str):
    """
    Get current status of a test run.
    
    Returns:
        Test run status
    """
    if test_run_id not in test_runs:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    return test_runs[test_run_id]


@router.get("/results/{test_run_id}")
async def get_test_results(test_run_id: str):
    """
    Get results of a completed test run.
    
    Returns:
        Test results
    """
    if test_run_id not in test_runs:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    test_run = test_runs[test_run_id]
    
    if test_run["status"] == "running":
        return {
            "test_run_id": test_run_id,
            "status": "running",
            "message": "Tests are still running"
        }
    
    results = test_run.get("results", {})
    
    return {
        "test_run_id": test_run_id,
        "status": test_run["status"],
        "test_type": test_run["test_type"],
        "started_at": test_run.get("started_at"),
        "completed_at": test_run.get("completed_at"),
        "summary": results.get("summary", {}),
        "tests": results.get("tests", []),
        "stdout": results.get("stdout", ""),
        "stderr": results.get("stderr", "")
    }


@router.get("/list")
async def list_test_runs(limit: int = 10):
    """
    List recent test runs.
    
    Returns:
        List of test runs
    """
    runs = list(test_runs.values())
    runs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    return runs[:limit]

