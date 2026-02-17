# Plan: Simplify DuplicationRecords constructor

**Status: DONE (55707f1)**

## Context
`DuplicationRecords.__init__` took 3 arguments: `record_paths`, `moved_dupes_path`, and `configs`. The caller in `main.py` extracted these from a `FoldersForScanResults` object. Passing the whole `FoldersForScanResults` object instead simplifies the call site and reduces coupling to internal attribute names.

## Changes

### 1. `DuplicationRecords.py`
- Changed `__init__(self, record_paths, moved_dupes_path, configs)` -> `__init__(self, folders, configs)`
- Extract paths internally:
  - `self.path_for_records = folders.record_folder_paths`
  - `self.moved_dupes_path = folders.moved_dupes_files_path`

### 2. `main.py` (line 24-26)
- `DuplicationRecords(folders_this_run.record_folder_paths, folders_this_run.moved_dupes_files_path, configs)` -> `DuplicationRecords(folders_this_run, configs)`

### 3. `tests/test_auto_move.py`
- `setup_env()` returns `(configs, folders)` instead of `(configs, record_paths, moved_dupes_path)`
- All 12 test functions updated to unpack as `configs, folders`
- All `DuplicationRecords(record_paths, moved_dupes_path, configs)` -> `DuplicationRecords(folders, configs)`
- All `record_paths.X` -> `folders.record_folder_paths.X`
- All `moved_dupes_path` -> `folders.moved_dupes_files_path`
- Removed unused `RecordFolders` import

### 4. `CLAUDE.md`
- Updated the `DuplicationRecords` init args description
