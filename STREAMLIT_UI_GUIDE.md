# Streamlit Test Runner UI Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit
# Or install all requirements:
pip install -r requirements.txt
```

### 2. Start Backend API
```bash
cd backend/ingestion
python router.py
# Or:
uvicorn router:app --host 0.0.0.0 --port 8000
```

### 3. Run Streamlit UI
```bash
streamlit run test_runner_ui.py
```

The UI will open in your browser at `http://localhost:8501`

## 🎨 Features

### Test Suite Selection
- **Unit Tests**: Individual component tests
- **Integration Tests**: Component interaction tests
- **E2E Tests**: End-to-end flow tests
- **All Tests**: Run everything

### Real-Time Progress
- Progress bar showing test execution
- Current test being run
- Status updates

### Results Display
- ✅ Passed tests (green)
- ❌ Failed tests (red) with error details
- Summary statistics (total, passed, failed, duration)
- Standard output and error logs

### Recent Test Runs
- View last 5 test runs in sidebar
- Quick status overview

## 📋 Usage

1. **Select Test Type**: Use the radio buttons in the sidebar
2. **Click Run**: Press the "Run Tests" button
3. **Monitor Progress**: Watch the progress bar and status
4. **Review Results**: See pass/fail status and any errors

## 🔧 Configuration

### Change API URL
Edit `test_runner_ui.py`:
```python
API_BASE_URL = "http://localhost:8000"  # Change this
```

### Customize UI
- Modify colors in the CSS section
- Add more metrics in `display_test_results()`
- Customize layout in `main()`

## 🐛 Troubleshooting

### "Cannot connect to API"
- Make sure backend is running on port 8000
- Check `API_BASE_URL` in the script
- Verify API health: `curl http://localhost:8000/api/v1/health`

### Tests Not Running
- Check backend logs for errors
- Verify test files exist in `tests/` directory
- Check pytest is installed: `pip install pytest`

### UI Not Updating
- Refresh the browser
- Check browser console for errors
- Restart Streamlit: `Ctrl+C` then `streamlit run test_runner_ui.py`

## 🎯 Next Steps

### Enhance UI
- Add test coverage visualization
- Add historical test run charts
- Add export functionality (CSV, JSON)
- Add test filtering/search

### Integration
- Add to CI/CD pipeline
- Schedule automated test runs
- Email notifications on failures

## 📝 Notes

- Tests run synchronously (one at a time)
- Maximum wait time: 5 minutes per test run
- Results are stored in session state (lost on refresh)
- For persistent storage, use the backend API's test run storage

