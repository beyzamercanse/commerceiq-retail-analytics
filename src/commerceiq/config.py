"""Local configuration; environment DATABASE_URL overrides .env."""
import os
from dotenv import load_dotenv

def database_url() -> str:
    load_dotenv(override=False)
    value = os.environ.get("DATABASE_URL", "").strip()
    if not value:
        raise ValueError("DATABASE_URL is required. Copy .env.example to .env.")
    return value
