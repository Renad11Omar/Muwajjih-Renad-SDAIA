.PHONY: install train test test-slow lint typecheck arch image image-size up down smoke bench regen-golden

install:
	python -m pip install -r requirements-dev.lock
	python -m pip install -e .
	python scripts/train_model.py

train:
	PYTHONPATH=src python scripts/train_model.py

test:
	PYTHONPATH=src pytest -m 'not slow' --cov=src/muwajjih/domain --cov=src/muwajjih/service --cov=src/muwajjih/api --cov-report=term-missing --cov-branch

test-slow:
	PYTHONPATH=src pytest -m slow -q

lint:
	ruff check .

format-check:
	ruff format --check .

typecheck:
	mypy src

arch:
	lint-imports

image:
	docker build --platform linux/amd64 -t muwajjih:dev .

image-size:
	docker image inspect muwajjih:dev --format '{{.Size}}' | awk '{printf "%.1f MB\n", $$1/1000000}'

up:
	docker compose up -d --build

down:
	docker compose down -v

smoke:
	curl -fsS http://localhost:8000/v1/health
	curl -fsS http://localhost:8000/v1/ready
	curl -fsS -X POST http://localhost:8000/v1/predict -H 'Content-Type: application/json' -d '{"complaint_id":"MWJ-DEMO-001","text":"هناك حريق قرب مدرسة"}'

bench:
	PYTHONPATH=src python scripts/benchmarks.py

regen-golden:
	APPROVE_GOLDEN_REGEN=1 PYTHONPATH=src python scripts/regen_golden.py
