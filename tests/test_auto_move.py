import hashlib
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from Configurations import Configurations
from FoldersForScanResults import FoldersForScanResults, RecordFolders
from DuplicationRecords import DuplicationRecords

def write_config(tmp_path, **overrides):
    values = {
        'file_extensions': '.jpg,.png',
        'max_file_size': '1073741824',
        'min_file_size': '0',
        'clean_up': 'yes',
        'move': 'yes',
        'folders': str(tmp_path / 'scan'),
        'location': str(tmp_path / 'results'),
        'moved_dupes_location': str(tmp_path / 'moved_dupes'),
    }
    values.update(overrides)

    config_text = textwrap.dedent(f"""\
        [supported_files]
        file_extensions = {values['file_extensions']}

        [file_sizes]
        max_file_size = {values['max_file_size']}
        min_file_size = {values['min_file_size']}

        [clean_up_previous_run]
        clean_up = {values['clean_up']}

        [move_duplicate_file]
        move = {values['move']}

        [location_for_moved_dupes]
        location = {values['moved_dupes_location']}

        [folders_to_scan]
        folders = {values['folders']}

        [location_for_scan_results]
        location = {values['location']}
    """)

    config_file = tmp_path / 'config.ini'
    config_file.write_text(config_text, encoding='utf-8')
    return config_file


def create_test_file(directory, name, content=b'duplicate content'):
    """Create a file with specific content for hash-controlled testing."""
    file_path = directory / name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)
    return file_path


def setup_env(tmp_path, **config_overrides):
    """Create config, folders, and return (configs, record_paths, moved_dupes_path) for testing."""
    config_file = write_config(tmp_path, **config_overrides)
    configs = Configurations(config_file)
    folders = FoldersForScanResults(configs)
    folders.set_up_folders()
    return configs, folders.record_folder_paths, folders.moved_dupes_files_path


def file_hash(file_path):
    with file_path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


# --- Move-mode tests ---

def test_first_occurrence_not_moved(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir, 'unique.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    # Record should exist in non_dupes_records, not in moved_dupes_records
    non_dupe_records = list(record_paths.non_dupes_records.glob("*.txt"))
    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    assert len(non_dupe_records) == 1
    assert len(moved_records) == 0
    # Original file should still exist
    assert (scan_dir / 'unique.jpg').exists()


def test_second_occurrence_moved(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    file1 = create_test_file(scan_dir / 'a', 'photo.jpg')
    file2 = create_test_file(scan_dir / 'b', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    # One file kept, one moved
    non_dupe_records = list(record_paths.non_dupes_records.glob("*.txt"))
    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    assert len(non_dupe_records) == 1
    assert len(moved_records) == 1

    # Exactly one of the two source files should be gone
    assert file1.exists() != file2.exists()


def test_third_occurrence_two_moved(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir / 'a', 'photo.jpg')
    create_test_file(scan_dir / 'b', 'photo.jpg')
    create_test_file(scan_dir / 'c', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    assert len(moved_records) == 1

    # moved_dupes_records record should have 2 lines (2nd and 3rd occurrence)
    lines = [l for l in moved_records[0].read_text(encoding='utf-8').splitlines() if l.strip()]
    assert len(lines) == 2


def test_moved_file_exists_at_destination(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir / 'a', 'photo.jpg')
    file2 = create_test_file(scan_dir / 'b', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    # Parse the moved_dupes_records record to find the destination
    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    line = moved_records[0].read_text(encoding='utf-8').splitlines()[0]
    _, destination = line.split(' -> ')

    assert Path(destination).exists()


def test_moved_file_removed_from_source(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir / 'a', 'photo.jpg')
    create_test_file(scan_dir / 'b', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    line = moved_records[0].read_text(encoding='utf-8').splitlines()[0]
    original, _ = line.split(' -> ')

    assert not Path(original).exists()


def test_moved_file_content_matches_original(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    content = b'identical image data'
    kept = create_test_file(scan_dir / 'a', 'photo.jpg', content)
    create_test_file(scan_dir / 'b', 'photo.jpg', content)

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    # Find which file was kept (the one that still exists)
    non_dupe_record = list(record_paths.non_dupes_records.glob("*.txt"))[0]
    kept_path = Path(non_dupe_record.read_text(encoding='utf-8').splitlines()[0])

    # Find the moved file
    deleted_record = list(record_paths.moved_dupes_records.glob("*.txt"))[0]
    _, dest = deleted_record.read_text(encoding='utf-8').splitlines()[0].split(' -> ')
    moved_path = Path(dest)

    assert file_hash(kept_path) == file_hash(moved_path)


def test_record_format_contains_arrow(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir / 'a', 'photo.jpg')
    create_test_file(scan_dir / 'b', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    for line in moved_records[0].read_text(encoding='utf-8').splitlines():
        if line.strip():
            assert ' -> ' in line


def test_dupes_folder_empty_in_move_mode(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir / 'a', 'photo.jpg')
    create_test_file(scan_dir / 'b', 'photo.jpg')
    create_test_file(scan_dir / 'c', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    assert list(record_paths.dupes_records.glob("*.txt")) == []


def test_different_paths_same_filename_no_collision(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    scan_dir = tmp_path / 'scan'
    create_test_file(scan_dir / 'folder1', 'photo.jpg')
    create_test_file(scan_dir / 'folder2', 'photo.jpg')
    create_test_file(scan_dir / 'folder3', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    # All moved files should exist at their destinations
    moved_records = list(record_paths.moved_dupes_records.glob("*.txt"))
    for line in moved_records[0].read_text(encoding='utf-8').splitlines():
        if line.strip():
            _, dest = line.split(' -> ')
            assert Path(dest).exists()


def test_move_disabled_does_not_move(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path, move='no')
    scan_dir = tmp_path / 'scan'
    file1 = create_test_file(scan_dir / 'a', 'photo.jpg')
    file2 = create_test_file(scan_dir / 'b', 'photo.jpg')

    dr = DuplicationRecords(record_paths, moved_dupes_path, configs)
    dr.analyze_folder(scan_dir)

    # Both source files should still exist
    assert file1.exists()
    assert file2.exists()
    # No moved_dupes_records records
    assert list(record_paths.moved_dupes_records.glob("*.txt")) == []
    # moved_dupes_files should be empty
    assert list(moved_dupes_path.rglob("*")) == []



# --- FoldersForScanResults tests ---

def test_moved_dupes_files_folder_created(tmp_path):
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)

    assert moved_dupes_path.exists()
    assert moved_dupes_path.is_dir()


def test_clean_up_does_not_remove_moved_dupes_files(tmp_path):
    # First run: create folders and add a file to moved_dupes_files
    configs, record_paths, moved_dupes_path = setup_env(tmp_path)
    marker = moved_dupes_path / 'marker.txt'
    marker.write_text('test', encoding='utf-8')

    # Second run with cleanup: moved_dupes_files should NOT be wiped
    folders = FoldersForScanResults(configs)
    folders.set_up_folders()

    assert moved_dupes_path.exists()
    assert marker.exists()
