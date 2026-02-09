# Plan: Switch from MD5 to SHA-256 for collision resistance — DONE (commit 568c5e8)

## Context
MD5 is not collision-resistant — it's possible (though unlikely in practice) for two different files to produce the same hash and be silently treated as duplicates. Switching to SHA-256 makes this cryptographically infeasible.

## Changes

### 1. `DuplicationRecords.py` (line 19)
Change `"md5"` to `"sha256"` in `_calculate_hash()`.

### 2. `CLAUDE.md` (lines 7, 44, 49)
Update references from "MD5" to "SHA-256".

That's it — the hash algorithm is only specified in one place in the application code, and record filenames are already just `{hash}.txt` so the longer SHA-256 hex string works without any other changes.

**Note:** Existing record files from previous runs used MD5 hashes. If `clean_up_previous_run` is set to `no`, old MD5-named records won't match new SHA-256-named records, so files would be re-evaluated as if new. With the current config (`clean_up = yes`), this is a non-issue.

## Verification
Run `python main.py` from the project directory. Check that record files in the output folder have 64-character hex names (SHA-256) instead of 32-character (MD5).
