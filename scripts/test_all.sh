#!/bin/bash

set -e
echo "Running all tests..."

cd backend
source venv/bin/activate

echo "Running unit tests..."
pytest tests/ -v --tb=short -q

echo "Running governance tests..."
pytest tests/test_governance.py -v

echo "All tests passed!"
