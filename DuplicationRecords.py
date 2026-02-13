import hashlib
import logging
import shutil
from pathlib import Path
from collections import namedtuple
from Configurations import Configurations


class DuplicationRecords:

    def __init__(self, paths, configs: Configurations):

        self.path_for_records = paths
        self.configs = configs

    def _calculate_hash(self, filepath: Path) -> str:
        
        try:
            with filepath.open("rb") as file_handle:
                file_hash = hashlib.file_digest(file_handle, "sha256").hexdigest()
        except PermissionError as e:
            logging.warning(f'Cannot access {filepath}: {e}')
            raise RuntimeError(f'Cannot access {filepath}: {e}') from e
        return file_hash
    
    def analyze_folder(self, folder_path: Path) -> None:
        
        if not folder_path.is_dir():
            logging.warning(f'{folder_path} does not exist')
            return

        logging.info(f'Analyzing files in {folder_path}')
        file_paths = folder_path.rglob("*")   # gives a generator with all sub-folders and files

        for path in file_paths:
            if not self._skip_file(path):
                self._analyze_file(path)

    def _skip_file(self, filepath: Path):
        if filepath.suffix not in self.configs.supported_file_types:
            logging.debug(f'Skipping file (or dir) {filepath} because its type is not supported')
            return True
    
        file_size = filepath.stat().st_size
        if self.configs.min_file_size <= file_size <= self.configs.max_file_size:
            return False
        logging.info(f'Skipping file {filepath} because its size is {file_size}')
        return True
       
    def _analyze_file(self, file_path: Path) -> None:
        
        try:
            record_filename = self._calculate_hash(file_path) + ".txt"
        except RuntimeError as e:
            logging.warning(e)
            return
        
        record_file_dupes = self.path_for_records.dupes / record_filename
        record_file_nondupes = self.path_for_records.non_dupes / record_filename
        record_file_deleted = self.path_for_records.deleted_dupes / record_filename
        
        if not self.configs.delete_duplicate_file:

            if record_file_dupes.exists():
                logging.info(f'Multiple duplicates found for: {file_path}')
                self._write_record(record_file_dupes, file_path)
                return
            
            if record_file_nondupes.exists():
                logging.info(f'One duplicate found for: {file_path}')
                self._write_record(record_file_nondupes, file_path)
                self._move_record_file(record_file_nondupes, record_file_dupes)
                return

            self._write_record(record_file_nondupes, file_path)

        else:
            if record_file_deleted.exists():
                logging.info(f'Multiple duplicates found, moving: {file_path}')
                moved_to = self._move_duplicate_file(file_path)
                self._write_delete_record(record_file_deleted, file_path, moved_to)
                return

            if record_file_nondupes.exists():
                logging.info(f'Duplicate found, moving: {file_path}')
                moved_to = self._move_duplicate_file(file_path)
                self._write_delete_record(record_file_deleted, file_path, moved_to)
                return

            self._write_record(record_file_nondupes, file_path)

    @staticmethod
    def _write_record(record_file: Path, file: Path):

        try:
            with record_file.open("a", encoding='utf-8') as f:
                logging.debug(f'Recording info for {file} into file {record_file}')
                f.write(str(file) + "\n")
        except Exception as e:
            logging.critical(f'Cannot write to {record_file}: {e}', exc_info=True)
            raise RuntimeError(f'Cannot write to {record_file}: {e}') from e

    def _move_duplicate_file(self, file_path: Path) -> Path:

        try:
            parts = file_path.parts
            if file_path.drive:
                drive_letter = file_path.drive.rstrip(':')
                relative = Path(drive_letter, *parts[1:])
            else:
                relative = Path(*parts[1:])

            destination = self.path_for_records.moved_duplicates / relative
            destination.parent.mkdir(parents=True, exist_ok=True)

            logging.info(f'Moving duplicate file {file_path} to {destination}')
            shutil.move(str(file_path), str(destination))
            return destination
        except Exception as e:
            logging.critical(f'Cannot move duplicate file {file_path}: {e}', exc_info=True)
            raise RuntimeError(f'Cannot move duplicate file {file_path}: {e}') from e

    @staticmethod
    def _write_delete_record(record_file: Path, original_path: Path, moved_path: Path):

        try:
            with record_file.open("a", encoding='utf-8') as f:
                logging.debug(f'Recording deletion info for {original_path} into {record_file}')
                f.write(f'{original_path} -> {moved_path}\n')
        except Exception as e:
            logging.critical(f'Cannot write to {record_file}: {e}', exc_info=True)
            raise RuntimeError(f'Cannot write to {record_file}: {e}') from e

    @staticmethod
    def _move_record_file(source: Path, target: Path):

        logging.info(f'Moving file from {source} to {target}')
        try:
            Path.rename(source, target)
        except Exception as e:
            logging.critical(f'Cannot move file from {source} to {target}: {e}', exc_info=True)
            raise RuntimeError(f'Cannot move file from {source} to {target}') from e
