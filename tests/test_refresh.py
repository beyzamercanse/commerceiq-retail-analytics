"""Audited refresh: failure records and idempotent execution boundaries."""

from pathlib import Path
from unittest.mock import patch

import pytest

from commerceiq.ops import refresh


@patch("commerceiq.ops.finish_run")
@patch("commerceiq.ops.subprocess.run")
@patch("commerceiq.ops.ingest_directory")
@patch("commerceiq.ops.start_run")
def test_refresh_tracks_success(start, ingest, command, finish):
    start.return_value = 19
    ingest.return_value = [("orders", "loaded", 3), ("payments", "skipped", 2)]
    assert refresh(
        "postgresql://test",
        Path("data/sample_olist"),
        project_dir=Path("analytics"),
        profiles_dir=Path("analytics"),
    ) == 19
    finish.assert_called_once_with(
        "postgresql://test",
        19,
        "success",
        loaded_files=1,
        skipped_files=1,
        loaded_rows=3,
    )
    assert command.call_args.kwargs["check"] is True


@patch("commerceiq.ops.finish_run")
@patch("commerceiq.ops.subprocess.run")
@patch("commerceiq.ops.ingest_directory")
@patch("commerceiq.ops.start_run")
def test_refresh_tracks_failed_dbt_build(start, ingest, command, finish):
    start.return_value = 21
    ingest.return_value = [("orders", "loaded", 3)]
    command.side_effect = OSError("dbt unavailable")
    with pytest.raises(OSError, match="dbt unavailable"):
        refresh("postgresql://test", Path("data/sample_olist"))
    finish.assert_called_once_with(
        "postgresql://test",
        21,
        "failed",
        loaded_files=1,
        skipped_files=0,
        loaded_rows=3,
        error_message="dbt unavailable",
    )
