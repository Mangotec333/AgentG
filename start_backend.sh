#!/bin/bash
cd "$(dirname "$0")"
cd backend/ingestion
python3 router.py
