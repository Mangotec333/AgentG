# Testing Guide - Streamlit UI

## 🚀 Quick Start

### Option 1: Automated Script (Easiest)
```bash
./test_ui.sh
```

This script will:
- Check if backend is running
- Install dependencies if needed
- Start backend if not running
- Start Streamlit UI
- Open browser automatically

### Option 2: Manual Start

**Terminal 1 - Start Backend:**
```bash
cd backend/ingestion
python router.py
```

**Terminal 2 - Start UI:**
```bash
streamlit run test_runner_ui.py
```

## 🧪 Testing Steps

### 1. Verify Backend is Running
```bash
curl http://localhost:8000/api/v1/health
```

Should return:
```json
{"status": "healthy", "service": "ingestion-api"}
```

### 2. Verify Test Runner API
```bash
curl http://localhost:8000/api/v1/tests/list
```

Should return list of test runs (may be empty initially).

### 3. Open Streamlit UI
- Browser should open automatically at `http://localhost:8501`
- Or manually navigate to that URL

### 4. Test the UI

#### Test 1: Run Unit Tests
1. Select "unit" in sidebar
2. Click "▶️ Run UNIT Tests"
3. Watch progress bar
4. View results

#### Test 2: Run All Tests
1. Select "all" in sidebar
2. Click "▶️ Run ALL Tests"
3. Wait for completion
4. Check summary statistics

#### Test 3: View Failed Tests
1. Run tests
2. Expand failed test details
3. Check error messages

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill process if needed
kill -9 $(lsof -ti:8000)

# Try starting again
cd backend/ingestion
python router.py
```

### Streamlit Not Starting
```bash
# Check if port 8501 is in use
lsof -ti:8501

# Kill process if needed
kill -9 $(lsof -ti:8501)

# Try starting again
streamlit run test_runner_ui.py
```

### API Connection Error
- Make sure backend is running on port 8000
- Check `API_BASE_URL` in `test_runner_ui.py`
- Verify: `curl http://localhost:8000/api/v1/health`

### Tests Not Running
- Check backend logs for errors
- Verify test files exist: `ls tests/unit/`
- Check pytest is installed: `pip list | grep pytest`

### Import Errors
```bash
# Install all dependencies
pip install -r requirements.txt
```

## ✅ Expected Results

### Successful Test Run
- Progress bar fills to 100%
- Summary shows: Total, Passed, Failed, Duration
- Passed tests shown in green
- Failed tests shown in red with error details

### Failed Test Run
- Some tests show as failed
- Error messages displayed
- Summary shows failed count > 0

## 📊 Test Results Interpretation

### All Tests Pass
```
Total: 10  ✅ Passed: 10  ❌ Failed: 0
Duration: 2.34s
```
✅ System is working correctly!

### Some Tests Fail
```
Total: 10  ✅ Passed: 8  ❌ Failed: 2
Duration: 2.45s
```
⚠️ Some components need attention. Check error messages.

### All Tests Fail
```
Total: 10  ✅ Passed: 0  ❌ Failed: 10
Duration: 0.12s
```
❌ Major issue. Check:
- Backend logs
- Test file imports
- Dependencies installed

## 🎯 Next Steps After Testing

1. **Fix Failing Tests**: Address any test failures
2. **Add More Tests**: Expand test coverage
3. **Enhance UI**: Add features like:
   - Test coverage visualization
   - Historical charts
   - Export functionality
4. **CI/CD Integration**: Add to automated pipeline

## 📝 Notes

- First run may take longer (imports, initialization)
- Tests run synchronously (one at a time)
- Maximum wait: 5 minutes per test run
- Results stored in session (refresh to clear)

