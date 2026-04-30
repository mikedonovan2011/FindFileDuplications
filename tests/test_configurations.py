import os
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from Configurations import Configurations


def write_config(tmp_path, **overrides):
    """Write a valid config.ini to tmp_path and return the Path.

    Keyword arguments override specific values in the config file.
    """
    values = {
        'file_extensions': '.jpg,.png',
        'max_file_size': '1073741824',
        'min_file_size': '10240',
        'clean_up': 'yes',
        'move': 'no',
        'folders': str(tmp_path),
        'location': str(tmp_path / 'scan_results'),
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

        [folders_to_scan]
        folders = {values['folders']}

        [location_for_scan_results]
        location = {values['location']}

        [location_for_moved_dupes]
        location = {values['moved_dupes_location']}
    """)

    config_file = tmp_path / 'config.ini'
    config_file.write_text(config_text, encoding='utf-8')
    return config_file


def test_valid_config_loads(tmp_path):
    config_file = write_config(tmp_path)
    cfg = Configurations(config_file)

    assert cfg.min_file_size == 10240
    assert cfg.max_file_size == 1073741824
    assert cfg.supported_file_types == ['.jpg', '.png']
    assert cfg.clean_up_previous_run is True
    assert cfg.move_duplicate_file is False
    assert cfg.folders_to_scan == [tmp_path.resolve()]
    assert cfg.location_for_scan_results == (tmp_path / 'scan_results').resolve()
    assert cfg.location_for_moved_dupes == (tmp_path / 'moved_dupes').resolve()


def test_missing_section_raises(tmp_path):
    config_text = textwrap.dedent(f"""\
        [supported_files]
        file_extensions = .jpg

        [file_sizes]
        max_file_size = 1073741824
        min_file_size = 0

        [clean_up_previous_run]
        clean_up = yes

        [move_duplicate_file]
        move = no

        [folders_to_scan]
        folders = {tmp_path}

        [location_for_scan_results]
        location = {tmp_path / 'scan_results'}
    """)
    config_file = tmp_path / 'config.ini'
    config_file.write_text(config_text, encoding='utf-8')

    with pytest.raises(RuntimeError, match='Missing required config sections'):
        Configurations(config_file)


def test_missing_config_file_raises(tmp_path):
    nonexistent = tmp_path / 'does_not_exist.ini'
    with pytest.raises(RuntimeError, match='not found'):
        Configurations(nonexistent)


@pytest.mark.skipif(sys.platform == 'win32', reason='Cannot reliably remove read permission on Windows')
def test_unreadable_config_file_raises(tmp_path):
    config_file = write_config(tmp_path)
    config_file.chmod(0o000)
    try:
        with pytest.raises(RuntimeError, match='not readable'):
            Configurations(config_file)
    finally:
        config_file.chmod(0o644)


def test_negative_min_file_size_raises(tmp_path):
    config_file = write_config(tmp_path, min_file_size='-1')
    with pytest.raises(RuntimeError, match='min_file_size cannot be negative'):
        Configurations(config_file)


def test_negative_max_file_size_raises(tmp_path):
    config_file = write_config(tmp_path, max_file_size='-1')
    with pytest.raises(RuntimeError, match='max_file_size cannot be negative'):
        Configurations(config_file)


def test_min_greater_than_max_raises(tmp_path):
    config_file = write_config(tmp_path, min_file_size='5000', max_file_size='5000')
    with pytest.raises(RuntimeError, match='must be less than'):
        Configurations(config_file)


def test_non_integer_min_file_size_raises(tmp_path):
    config_file = write_config(tmp_path, min_file_size='abc')
    with pytest.raises(RuntimeError, match='min_file_size must be an integer'):
        Configurations(config_file)


def test_non_integer_max_file_size_raises(tmp_path):
    config_file = write_config(tmp_path, max_file_size='abc')
    with pytest.raises(RuntimeError, match='max_file_size must be an integer'):
        Configurations(config_file)


def test_empty_folders_to_scan_raises(tmp_path):
    config_file = write_config(tmp_path, folders='')
    with pytest.raises(RuntimeError, match='No folders to scan'):
        Configurations(config_file)


def test_default_values(tmp_path):
    """Omit optional keys and verify defaults are used."""
    config_text = textwrap.dedent(f"""\
        [supported_files]

        [file_sizes]

        [clean_up_previous_run]

        [move_duplicate_file]

        [folders_to_scan]
        folders = {tmp_path}

        [location_for_scan_results]

        [location_for_moved_dupes]
    """)
    config_file = tmp_path / 'config.ini'
    config_file.write_text(config_text, encoding='utf-8')

    cfg = Configurations(config_file)

    assert cfg.min_file_size == 0
    assert cfg.max_file_size == 1073741824
    assert cfg.clean_up_previous_run is True
    assert cfg.move_duplicate_file is False
    assert cfg.location_for_scan_results == Path('scan_results').resolve()
    assert cfg.location_for_moved_dupes == Path('moved_dupes_files').resolve()


def test_clean_up_previous_run_bool(tmp_path):
    config_file = write_config(tmp_path, clean_up='no')
    cfg = Configurations(config_file)
    assert cfg.clean_up_previous_run is False

    config_file = write_config(tmp_path, clean_up='yes')
    cfg = Configurations(config_file)
    assert cfg.clean_up_previous_run is True


def test_supported_file_types_parsed(tmp_path):
    config_file = write_config(tmp_path, file_extensions='.bmp, .gif, .webp')
    cfg = Configurations(config_file)
    assert cfg.supported_file_types == ['.bmp', '.gif', '.webp']
