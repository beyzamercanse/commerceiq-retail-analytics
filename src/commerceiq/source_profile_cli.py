"""Command to validate the nine CSVs before loading PostgreSQL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from commerceiq.source_profile import format_report, inspect_directory


def main() -> None:
    parser = argparse.ArgumentParser(prog="commerceiq-profile")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--min-orders", type=int, default=1)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        report = inspect_directory(args.data_dir, min_orders=args.min_orders)
        body = format_report(report)
        print(body)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(body + "\n", encoding="utf-8")
        if report["status"] != "pass":
            raise SystemExit(1)
    except (OSError, ValueError) as exc:
        print(f"Source inspection error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
