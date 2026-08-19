.PHONY: help setup backend frontend docker-up docker-down test clean

help:
	@echo "EduMind AI Platform Commands:"
	@echo "  make setup      - Full setup"
	@echo "  make backend    - Run backend dev server"
	@echo "  make frontend   - Run frontend dev server"
	@echo "  make docker-up  - Start with Docker"
	@echo "  make docker-down- Stop Docker"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Clean temp files"

setup:
	@echo "Setting up EduMind AI..."
	cd backend && python -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt && \
		python -m spacy download en_core_web_sm
	cd frontend && npm install
	@echo "Setup complete!"

backend:
	cd backend && . venv/bin/activate && \
		uvicorn main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

docker-up:
	docker-compose up --build -d
	@echo "Platform running at http://localhost:3000"
	@echo "API docs at http://localhost:8000/docs"

docker-down:
	docker-compose down

test:
	cd backend && . venv/bin/activate && \
		pytest tests/ -v --tb=short

test-governance:
	cd backend && . venv/bin/activate && \
		pytest tests/test_governance.py -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/uploads/* 2>/dev/null || true
	rm -rf backend/logs/* 2>/dev/null || true
	@echo "Cleaned!"

logs:
	tail -f backend/logs/*.log

seed:
	cd backend && . venv/bin/activate && \
		python scripts/seed_database.py
