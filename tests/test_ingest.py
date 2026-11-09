import csv
from pathlib import Path

import pytest

from commerceiq.ingest import csv_records, sha256_file


def test_sha256_is_content_based(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_bytes(b"a,b\n1,2\n")
    b.write_bytes(b"a,b\n1,2\n")
    assert sha256_file(a) == sha256_file(b)
    b.write_bytes(b"a,b\n1,3\n")
    assert sha256_file(a) != sha256_file(b)


def test_csv_records_preserve_empty_strings_and_quoted_commas(tmp_path: Path):
    csv_file = tmp_path / "sample.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "label", "notes"])
        writer.writerow(["1", "hello, world", ""])
        writer.writerow(["2", "", "test"])
    assert list(csv_records(csv_file, ("id", "label", "notes"))) == [
        (1, ("1", "hello, world", "")),
        (2, ("2", "", "test")),
    ]


def test_csv_header_mismatch_is_rejected(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("different,column\na,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Schema mismatch"):
        list(csv_records(path, ("id", "column")))


def test_csv_extra_fields_are_rejected(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("id,label\n1,foo,bar\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed CSV"):
        list(csv_records(path, ("id", "label")))
