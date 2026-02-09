# Plan: Add integrity check for non_dupes records at startup — DONE (commits 80ab472, d3574f3)

## Context
If the process is interrupted between writing a path to a `non_dupes` record and moving it to `dupes`, a record with 2+ paths can be left stranded in `non_dupes`. Empty record files can also be left behind. This feature adds a self-healing check at startup that detects and fixes these inconsistencies.

## Changes

### 1. `RecordRepair.py` — New `RecordRepair` class
Extracted from `DuplicationRecords` into its own class with a `repair()` method that iterates all `.txt` files in `non_dupes/`:
- **0 lines:** deletes the empty record
- **2+ lines:** moves the record from `non_dupes/` to `dupes/`
- **1 line:** valid, skipped
- Raises `RuntimeError` on failure (matching existing error pattern)

### 2. `main.py` — Call the repair before scanning
Creates a `RecordRepair` instance and calls `repair()` when `clean_up_previous_run` is `no` (when `clean_up` is `yes`, the folders are wiped anyway so there's nothing to repair).

## Files modified
- `RecordRepair.py` — new file with `RecordRepair` class
- `DuplicationRecords.py` — removed `repair_nondupes()` method
- `main.py` — imports and uses `RecordRepair`
- `CLAUDE.md` — documents new module

## Verification
1. Set `clean_up = no` in `config.ini`
2. Run `python main.py` once normally
3. Manually create an empty `.txt` file in `non_dupes/` and edit another to have two lines
4. Run `python main.py` again
5. Confirm: empty file deleted, multi-line file moved to `dupes/`, both logged
