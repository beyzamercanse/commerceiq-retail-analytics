# Data contracts

The ingestion layer recognizes nine Olist source CSVs, listed verbatim in `src/commerceiq/sources.py`. Headers must match exactly. An incorrect column count or name fails the entire file transaction. All source fields are raw text, preserving precision and empty strings for later dbt casting.

Every row also contains `_source_sha256`, `_row_number` and `_loaded_at`.

`raw.source_files` tracks `source_name`, `file_sha256`, `file_name`, `row_count` and `loaded_at`. Source rows and their audit record commit atomically.