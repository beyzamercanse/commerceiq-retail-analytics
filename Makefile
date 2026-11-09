.PHONY: setup db ingest status test lint integration refresh dashboard reporting
setup:
	python -m pip install -e '.[dev,dashboard]' 'dbt-postgres>=1.9,<2'
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
refresh:
	commerceiq-refresh --data-dir data/sample_olist
dashboard:
	streamlit run dashboard/app.py
reporting:
	pytest -o addopts= -m reporting
