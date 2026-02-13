# Plan: Recoverable Auto-Delete of Duplicate Files

**Status:** DONE (2a0f64b, ea30cf2, 735729f, 30b4117, 6ce7581)

## Context

The `delete_duplicate_file` config flag exists but is not implemented (line 77 of `DuplicationRecords.py` is a placeholder). The `deleted_dupes` output folder is already created but never populated. The user wants duplicate files **moved** to a recovery location (not permanently deleted) so they can be restored if needed.

## Approach

When `delete_duplicate_file = yes`, the second and subsequent files matching a hash are **moved** into a `moved_duplicates/` folder under `location_for_scan_results`. The original directory structure is preserved inside that folder so the user can see where each file came from and easily restore it. A record in `deleted_dupes/{hash}.txt` logs each move with an `original -> destination` format for auditing.

### Delete-mode behavior:
| Occurrence | Action |
|---|---|
| 1st (unique) | Keep file, write record to `non_dupes/` (same as today) |
| 2nd (first dup) | **Move file** to `moved_duplicates/`, create record in `deleted_dupes/` |
| 3rd+ | **Move file** to `moved_duplicates/`, append to `deleted_dupes/` record |

The `dupes/` folder is **not used** in delete mode. `non_dupes/` = kept files, `deleted_dupes/` = moved files with recovery info.

### Path preservation example:
```
Original:    C:\Users\mike\Photos\vacation\img001.jpg
Moved to:    {scan_results}\moved_duplicates\C\Users\mike\Photos\vacation\img001.jpg
```
This eliminates filename collisions and makes recovery obvious.

### deleted_dupes record format:
```
C:\Users\mike\Photos\vacation\img001.jpg -> C:\scan_results\moved_duplicates\C\Users\mike\Photos\vacation\img001.jpg
```

## Files to Change

### 1. `FoldersForScanResults.py` — Add `moved_duplicates` folder
- Add `moved_duplicates` as 4th field to `Folders` namedtuple (line 8)
- Add the path in `__init__` (line 16-19)
- No changes needed to `_clean_up_records` or `_create_folders` — they iterate `self.folders` so the new folder is automatically included

### 2. `DuplicationRecords.py` — Implement deletion logic
- Add `import shutil` (for cross-drive moves; `Path.rename` fails across drives on Windows)
- Add `_move_duplicate_file(file_path) -> Path` method:
  - Strips drive/root from absolute path to create relative structure
  - Creates parent dirs under `moved_duplicates/`
  - Uses `shutil.move()` to relocate the file
  - Returns destination path
  - Follows existing error pattern (log + raise RuntimeError)
- Add `_write_delete_record(record_file, original_path, moved_path)` static method:
  - Appends `{original} -> {destination}\n` to the record file
  - Same error pattern as `_write_record`
- Replace placeholder `else` block (line 76-77) with:
  - If `deleted_dupes` record exists → 3rd+ dup, move file + append record
  - If `non_dupes` record exists → 2nd dup, move file + create `deleted_dupes` record
  - Otherwise → 1st occurrence, write `non_dupes` record (keep file)

### 3. `RecordRepair.py` — Handle `deleted_dupes` records
- Add a second repair pass after the existing `non_dupes` pass
- Only repair: delete empty `deleted_dupes` record files (0 lines)
- Do NOT attempt to reconcile `moved_duplicates/` contents (too complex for initial implementation)

### 4. `config.ini` — Update comment (line 22)
- Change from "Not implemented" to describe the move-to-recovery behavior

### 5. `CLAUDE.md` — Update architecture docs
- Document delete-mode flow, `moved_duplicates` folder, and record format

### 6. `tests/test_auto_delete.py` — New test file
Key test cases:
- First occurrence is kept (not moved), `non_dupes` record created
- Second occurrence is moved, `deleted_dupes` record created with arrow format
- Third occurrence is moved, `deleted_dupes` record has two lines
- Moved file exists at destination and is gone from source
- Moved file content matches original (hash check)
- `dupes/` folder stays empty in delete mode
- Different files with same name in different dirs don't collide
- `delete=no` doesn't move anything (regression)
- Empty `deleted_dupes` records cleaned by RecordRepair
- `moved_duplicates` folder created/cleaned by FoldersForScanResults
