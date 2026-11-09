.PHONY: setup db ingest status test lint integration
setup:
	python -m pip install -e '.[dev]'
db:
	docker compose up -d --wait
ingest:
	commerceiq ingest --data-dir data/sample_olist --strict
status:
	commerceiq status
test:
	pytest
lint:
	ruff check .
integration:
	pytest -o addopts= -m integration
