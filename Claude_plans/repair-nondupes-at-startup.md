# Plan: Add integrity check for non_dupes records at startup

## Context
If the process is interrupted between writing a path to a `non_dupes` record and moving it to `dupes`, a record with 2+ paths can be left stranded in `non_dupes`. This feature adds a self-healing check at startup that detects and fixes these inconsistencies.

## Changes

### 1. `DuplicationRecords.py` — Add `repair_nondupes()` method
Add a new public method to `DuplicationRecords` that:
- Iterates over all `.txt` files in `non_dupes/`
- Reads each file and counts the number of lines (paths)
- If a record has 2+ lines, moves it from `non_dupes/` to `dupes/` using the existing `_move_record_file()` method
- Logs each repair action at INFO level

### 2. `main.py` — Call the repair method before scanning
After creating the `DuplicationRecords` instance (line 20) and before the scan loop (line 22), call `duplication_records.repair_nondupes()`. This runs only when `clean_up_previous_run` is `no` (when `clean_up` is `yes`, the folders are wiped anyway so there's nothing to repair).

## Files modified
- `DuplicationRecords.py` — added `repair_nondupes()` method
- `main.py` — added call to `repair_nondupes()` guarded by `not configs.clean_up_previous_run`

## Verification
1. Set `clean_up = no` in `config.ini`
2. Run `python main.py` once normally
3. Manually edit a record file in `non_dupes/` to have two lines (simulating an interrupted run)
4. Run `python main.py` again
5. Confirm the tampered record was moved to `dupes/` and a log entry was written
