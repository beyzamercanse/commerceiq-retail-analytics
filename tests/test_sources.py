from pathlib import Path

import pytest

from commerceiq.sources import SOURCES, source_files


def test_source_names_and_tables_are_unique():
    assert len(SOURCES) == 9
    assert len({source.table for source in SOURCES}) == len(SOURCES)
    assert len({source.filename for source in SOURCES}) == len(SOURCES)


def test_every_column_name_is_unique_in_its_table():
    for source in SOURCES:
        assert len(set(source.columns)) == len(source.columns)


def test_source_files_ignores_unknown_files(tmp_path: Path):
    (tmp_path / "unknown.csv").write_text("hello\nworld\n")
    assert source_files(tmp_path) == []


def test_strict_mode_reports_missing_sources(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Missing required Olist files"):
        source_files(tmp_path, strict=True)
