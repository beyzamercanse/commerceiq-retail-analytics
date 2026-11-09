"""Source CSV profiling covers real schema contracts with synthetic fixtures."""

import csv
from pathlib import Path

from commerceiq.source_profile import inspect_directory


DATA = Path(__file__).resolve().parents[1] / "data" / "sample_olist"


def test_synthetic_olist_complete():
    report = inspect_directory(DATA, min_orders=3)
    assert report["status"] == "pass", report
    assert len(report["sources"]) == 9
    assert report["order_rows"] == 3
    assert report["sources"]["payments"]["rows"] == 3


def test_scale_guard_rejects_fixture():
    report = inspect_directory(DATA, min_orders=90000)
    assert report["status"] == "fail"
    assert any("minimum" in issue for issue in report["failures"])


def test_duplicate_order_detected(tmp_path: Path):
    for source in DATA.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    path = tmp_path / "olist_orders_dataset.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = list(csv.reader(handle))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows([*reader, reader[1]])
    report = inspect_directory(tmp_path, min_orders=3)
    assert report["status"] == "fail"
    assert report["sources"]["orders"]["duplicate_business_keys"] == 1


def test_missing_file_detected(tmp_path: Path):
    report = inspect_directory(tmp_path, min_orders=0)
    assert report["status"] == "fail"
    assert len(report["failures"]) == 9
