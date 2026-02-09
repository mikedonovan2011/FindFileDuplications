# Plan: Refactor Configurations for testability + write pytest tests

## Status: DONE (commit 09c4d02)

## Context
`Configurations.__init__` hardcoded its config file path via `Path(__file__)`, making it impossible to test with different config contents without monkeypatching. Adding an optional `config_file` parameter makes the class directly testable.

## Changes

### 1. Refactor `Configurations.__init__` to accept optional path
**File:** `Configurations.py`

Changed `__init__(self)` to `__init__(self, config_file=None)` with fallback to the original `Path(__file__).resolve().parent / 'config.ini'`. All existing callers pass no arguments, so behavior is unchanged.

### 2. Created pytest test suite
**File:** `tests/test_configurations.py` (new file)

Helper function writes a valid `config.ini` to `tmp_path` and returns the path. Individual tests override specific values.

Tests written:
- **test_valid_config_loads** — valid config, all properties return expected values
- **test_missing_config_file_raises** — nonexistent path raises RuntimeError
- **test_unreadable_config_file_raises** — (skipped on Windows) permission-denied raises RuntimeError
- **test_negative_min_file_size_raises** — min_file_size = -1 raises RuntimeError
- **test_negative_max_file_size_raises** — max_file_size = -1 raises RuntimeError
- **test_min_greater_than_max_raises** — min >= max raises RuntimeError
- **test_empty_folders_to_scan_raises** — empty folders value raises RuntimeError
- **test_default_values** — omit optional keys, verify defaults are used
- **test_clean_up_previous_run_bool** — yes/no parsing works
- **test_supported_file_types_parsed** — comma-separated string becomes list

### 3. Added tests/__init__.py
**File:** `tests/__init__.py` (new, empty)

## Files modified
- `Configurations.py` — one-line change to `__init__` signature
- `tests/__init__.py` — new empty file
- `tests/test_configurations.py` — new file with 10 tests

## Verification
Result: 9 passed, 1 skipped (unreadable file test correctly skipped on Windows)
