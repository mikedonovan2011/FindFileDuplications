# Plan: Standardize logging and exception handling — DONE (d9afbe5)

## Context
Logging and exception handling patterns were inconsistent across the codebase. Some errors were logged before raising, some weren't. Some used `exc_info=True`, some didn't. One exception type mismatch meant a missing config.ini produced a traceback. The duplicated `_move_record_file` methods had inconsistent logging.

## Target pattern
- **Log critical with `exc_info=True`, then raise `RuntimeError`** — for all fatal errors
- **Log warning, then continue** — for non-fatal errors (e.g., permission error on a single file)
- **Single log entry per error** — not two

## Changes

### 1. `Configurations.py`
- Changed `raise FileNotFoundError(message)` to `raise RuntimeError(message)` so main.py's `except RuntimeError` catches it
- Added `logging.critical(...)` before each `raise RuntimeError` in `_validate_file_sizes()` to match the standard pattern

### 2. `DuplicationRecords.py`
- Added `logging.warning(...)` before raising in `_calculate_hash`, since this error is caught in `_analyze_file` and skipped (non-fatal)
- Changed `logging.error(e)` to `logging.warning(e)` in `_analyze_file` — this is a skip-and-continue path, WARNING is the appropriate level
- Added `exc_info=True` to the `logging.critical()` call in `_write_record` for traceback in the log
- Consolidated the two `logging.critical()` calls into one with `exc_info=True` in `_move_record_file`

### 3. `RecordRepair.py`
- Added `exc_info=True` to the `logging.critical()` call in `_delete_record`
- Consolidated the two `logging.critical()` calls into one with `exc_info=True` in `_move_record_file`
