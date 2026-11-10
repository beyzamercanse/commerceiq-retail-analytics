# Dashboard-only image. No writer credentials or dbt required.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY dashboard/ ./dashboard/
COPY .streamlit/config.toml ./.streamlit/config.toml
EXPOSE 8501
# Fail closed if the warehouse or limited database account is unavailable.
CMD ["sh", "-c", "python -m commerceiq.deployment_check && exec streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true"]
