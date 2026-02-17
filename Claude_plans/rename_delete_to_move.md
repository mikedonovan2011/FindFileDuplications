# Plan: Rename "delete" terminology to "move" for duplicate handling

**Status: DONE (ae9041b)**

## Context
The codebase confusingly uses both "delete" and "move" to describe the same operation — relocating duplicate files to a recovery folder. Consistent "move" terminology throughout since the files are moved, not deleted.

## Changes

### 1. `config.ini`
- Renamed section `[delete_duplicate_file]` → `[move_duplicate_file]`
- Renamed key `delete = yes` → `move = yes`
- Updated comments: "when delete_duplicate_file is enabled" → "when move_duplicate_file is enabled"

### 2. `Configurations.py`
- Renamed property `delete_duplicate_file` → `move_duplicate_file`
- Updated to read from `[move_duplicate_file]` section with key `move`

### 3. `DuplicationRecords.py`
- `self.configs.delete_duplicate_file` → `self.configs.move_duplicate_file`
- `_analyze_file_with_deletion` → `_analyze_file_with_moving`
- `_analyze_file_without_deletion` → `_analyze_file_without_moving`
- `record_file_deleted` → `record_file_moved`
- `_write_delete_record` → `_write_move_record`
- Log message: "Recording deletion info" → "Recording move info"

### 4. `tests/test_auto_delete.py` → `tests/test_auto_move.py`
- Renamed file
- Config helper: `'delete': 'yes'` → `'move': 'yes'`
- Config string: `[delete_duplicate_file]` / `delete =` → `[move_duplicate_file]` / `move =`
- Variable `deleted_records` → `moved_records` (all occurrences)
- `test_dupes_folder_empty_in_delete_mode` → `test_dupes_folder_empty_in_move_mode`
- `test_delete_off_does_not_move` → `test_move_disabled_does_not_move`

### 5. `tests/test_configurations.py`
- Config helper: `'delete': 'no'` → `'move': 'no'`
- Config string: `[delete_duplicate_file]` / `delete =` → `[move_duplicate_file]` / `move =`
- Assertions: `cfg.delete_duplicate_file` → `cfg.move_duplicate_file`

### 6. `CLAUDE.md`
- All references updated to match new naming
