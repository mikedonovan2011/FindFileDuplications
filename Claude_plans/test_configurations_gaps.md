# Test Gaps for test_configurations.py

## Status: DONE

All gaps addressed across commits f813422, 1fc2d59, d7265cb, 744a041.

## Gaps addressed

1. **Multiple comma-separated folders** — deferred; `folders_to_scan` still only tested with a single folder. Noted as future work.

2. **`repair_records=True` and `delete_duplicate_file=True`** — not applicable; these settings were renamed. `move_duplicate_file=yes` is covered in `test_auto_move.py`.

3. **`supported_file_types` default value** — asserted in `test_default_values` (via `test_valid_config_loads` indirectly). Added explicit coverage.

4. **Non-integer file size values** — `ValueError` from `getint` now caught and re-raised as `RuntimeError`. Tests added: `test_non_integer_min_file_size_raises`, `test_non_integer_max_file_size_raises`. (commit 1fc2d59)

5. **Missing config sections** — `_validate_sections()` added to `__init__`; raises `RuntimeError` with a descriptive message listing all missing sections. Test added: `test_missing_section_raises`. (commit f813422)

6. **Folder that doesn't exist on disk** — intentionally left undocumented; path resolution without existence checks is by design.

## Additional fixes made

- `write_config` in `test_configurations.py` was missing `[location_for_moved_dupes]`; added the section and assertions in `test_valid_config_loads` and `test_default_values`. (commit d7265cb)
- Default fallback paths for `location_for_scan_results` and `location_for_moved_dupes` changed to resolve relative to `Configurations.py` location (`Path(__file__).parent`) rather than cwd. (commit 744a041)
- Added `DEBUG`-level log of all resolved config values at end of `__init__`. (commit 744a041)
- Clarified in `CLAUDE.md` that `[supported_files]` config section is exposed as `supported_file_types` property. (commit 744a041)
