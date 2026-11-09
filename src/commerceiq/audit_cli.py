"""Console command producing machine-readable warehouse integrity evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from commerceiq.audit import run_audit
from commerceiq.config import database_url


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="commerceiq-audit", description="Check warehouse counts and model consistency"
    )
    parser.add_argument("--out", type=Path, help="Optional JSON report location")
    parser.add_argument("--min-orders", type=int, default=1)
    args = parser.parse_args()

    try:
        report = run_audit(database_url(), min_orders=args.min_orders)
        serialized = json.dumps(report, indent=2)
        print(serialized)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(serialized + "\n", encoding="utf-8")
        if report["status"] != "pass":
            raise SystemExit(1)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Audit could not run: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
