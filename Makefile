.PHONY: install run test clean

install:
	pip install -r backend/requirements.txt

run:
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	cd backend && python -m pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
