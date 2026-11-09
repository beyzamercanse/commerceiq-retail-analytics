"""CLI entry point for an audited ingestion and dbt warehouse refresh."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from commerceiq.config import database_url
from commerceiq.ops import refresh


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="commerceiq-refresh",
        description="Ingest Olist CSVs, run dbt and persist a pipeline audit.",
    )
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--project-dir", default=Path("analytics"), type=Path)
    parser.add_argument("--profiles-dir", default=Path("analytics"), type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    try:
        run_id = refresh(
            database_url(),
            args.data_dir,
            strict=not args.allow_partial,
            project_dir=args.project_dir,
            profiles_dir=args.profiles_dir,
        )
    except Exception as exc:
        print(f"Refresh failed ({type(exc).__name__}): {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"Refresh succeeded. Audited run_id={run_id}")


if __name__ == "__main__":
    main()
