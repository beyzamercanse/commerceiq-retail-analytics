# Dashboard-only image. No write credentials or dbt are required for this service.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY dashboard/ ./dashboard/
COPY .streamlit/config.toml ./.streamlit/config.toml
EXPOSE 8501
# Railway injects PORT. This image also works locally on the default 8501.
CMD ["sh", "-c", "exec streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true"]
