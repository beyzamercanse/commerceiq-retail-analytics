"""CommerceIQ command-line interface."""
import argparse
from pathlib import Path
import sys

import psycopg

from commerceiq.config import database_url
from commerceiq.ingest import ingest_directory, init_database, source_status
from commerceiq.sources import SOURCES


def main() -> None:
    parser = argparse.ArgumentParser(prog="commerceiq", description="CommerceIQ raw data tools")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db", help="Initialize raw tables")
    ingest = commands.add_parser("ingest", help="Ingest Olist CSV files")
    ingest.add_argument("--data-dir", required=True, type=Path)
    ingest.add_argument("--strict", action="store_true")
    commands.add_parser("status", help="Summarize source batches")
    commands.add_parser("sources", help="List required filenames")
    args = parser.parse_args()

    if args.command == "sources":
        for item in SOURCES:
            print(f"{item.filename} -> raw.{item.table}")
        return

    try:
        dsn = database_url()
        if args.command == "init-db":
            with psycopg.connect(dsn) as conn:
                init_database(conn)
            print("Raw schema initialized.")
        elif args.command == "ingest":
            for table, status, count in ingest_directory(dsn, args.data_dir, strict=args.strict):
                print(f"raw.{table}: {status} ({count:,} rows)")
        elif args.command == "status":
            rows = source_status(dsn)
            if not rows:
                print("No sources ingested.")
            for table, files, count in rows:
                print(f"raw.{table}: {files} batch(es), {count:,} rows")
    except (OSError, ValueError, psycopg.Error, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
