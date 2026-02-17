# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Duplicate file detection utility. Scans configured directories recursively, computes SHA-256 hashes, and categorizes files as unique or duplicate by writing text-based record files. Currently targets image files but the supported types are configurable. Licensed under GPLv3.

## Commands

```bash
# Run the application
python main.py

# Run tests
pytest tests/

# Install dependencies
pip install -r requirements.txt
```

No build step required — pure Python with only standard library dependencies. The virtual environment is at `.venv/`. The only pip dependency is `pytest`.

## Configuration

All runtime settings live in `config.ini` (loaded relative to `Configurations.py`'s location, not the working directory):
- `folders_to_scan` — comma-separated list of directories to analyze
- `location_for_scan_results` — where output folders are created
- `supported_files` — file extensions to process (whitespace around commas is stripped)
- `file_sizes` — min/max byte thresholds for skipping files (validated at startup: non-negative, min < max)
- `clean_up_previous_run` — whether to wipe previous output before starting
- `delete_duplicate_file` — when `yes`, duplicates are moved to the `location_for_moved_dupes` folder for recovery instead of being left in place
- `location_for_moved_dupes` — where moved duplicate files are stored (separate from records, not cleaned up by `clean_up_previous_run`)

## Architecture

Four modules with clear separation of concerns:

**`main.py`** — Entry point. Initializes logging, loads config, sets up output folders, then iterates `folders_to_scan` calling `DuplicationRecords.analyze_folder()` on each. All phases (config, folder setup, scan) are wrapped in try/except `RuntimeError` for graceful exit via `sys.exit()`.

**`Configurations.py`** — `Configurations` class. Wraps `configparser` to read `config.ini`. Exposes all settings as typed properties (int, bool, list, Path). Resolves folder paths to absolute via `Path.resolve()`. Validates file size constraints at init.

**`FoldersForScanResults.py`** — `FoldersForScanResults` class. Manages the output directory structure. Uses a `RecordFolders` namedtuple with three fields: `non_dupes_records`, `dupes_records`, `moved_dupes_records`. The `moved_dupes_files` path is stored separately from `location_for_moved_dupes` config. Cleanup only wipes the three record folders, never `moved_dupes_files`. Cleanup errors propagate up rather than being swallowed per-folder.

**`DuplicationRecords.py`** — `DuplicationRecords` class. Core logic. For each folder, recursively walks files via `rglob("*")`, filters by extension and size, computes SHA-256 hash, then dispatches to one of two mode-specific methods:

*`_analyze_file_without_deletion`* (`delete_duplicate_file = no`):
1. If hash record exists in `dupes_records/` — append path (3rd+ occurrence)
2. If hash record exists in `non_dupes_records/` — append path, then move record to `dupes_records/` (2nd occurrence)
3. Otherwise — create new record in `non_dupes_records/` (1st occurrence)

*`_analyze_file_with_deletion`* (`delete_duplicate_file = yes`):
1. If hash record exists in `moved_dupes_records/` — move file to `moved_dupes_files/`, append to record (3rd+ occurrence)
2. If hash record exists in `non_dupes_records/` — move file to `moved_dupes_files/`, create record in `moved_dupes_records/` (2nd occurrence)
3. Otherwise — keep file, create new record in `non_dupes_records/` (1st occurrence)

Record files are named `{sha256_hash}.txt`. In normal mode they contain one file path per line. In delete mode, `moved_dupes_records/` records use the format `{original_path} -> {moved_path}` per line. Moved files preserve their original directory structure under `moved_dupes_files/`.

## Error Handling

All errors in `DuplicationRecords` (`_write_record`, `_move_record_file`, `_move_duplicate_file`, `_write_delete_record`, `_calculate_hash`) raise `RuntimeError` after logging. These propagate to `main()` which catches them and exits cleanly. The same pattern applies to config loading and folder setup.
