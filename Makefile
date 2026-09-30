.PHONY: install-backend install-frontend build test run-backend qualify inspect-data corpus index classifier

install-backend:
	python -m pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

build:
	cd frontend && npm run build

test:
	cd backend && python -m compileall -q app
	python -m pytest -q

run-backend:
	uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

inspect-data:
	python scripts/inspect_datasets.py

corpus:
	python scripts/build_corpus.py --min-emails 10000 --limit 10000

index:
	python scripts/build_index.py

classifier:
	python scripts/train_injection_model.py --root data/raw

qualify:
	python scripts/qualify.py
