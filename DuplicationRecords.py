from pathlib import Path
import hashlib
import logging
import sys
from collections import namedtuple


class DuplicationRecords:

    def __init__(self, paths):

        self.path_for_records = paths

    def _calculate_hash(self, filepath):
        try:
            with filepath.open("rb") as file_handle:
                file_hash = hashlib.file_digest(file_handle, "md5").hexdigest()
        except PermissionError as e:
            logging.critical(e, exc_info=True)
            logging.critical(f'Cannot access {filepath}')
            sys.exit(f'Exiting because of permission error with {filepath}')
        return file_hash
       
    def analyze_file(self, file_path):
        
        record_filename = self._calculate_hash(file_path) + ".txt"
        record_file_dupes = self.path_for_records.dupes / record_filename
        record_file_nondupes = self.path_for_records.non_dupes / record_filename
        
        if record_file_dupes.exists():
            logging.info(f'Duplicate found for: {file_path}')
            self._write_record(record_file_dupes, file_path)
            return
        
        if record_file_nondupes.exists():
            logging.info(f'Duplicate found for: {file_path}')
            self._write_record(record_file_nondupes, file_path)
            self._move_record_file(record_file_nondupes, record_file_dupes)
            return

        self._write_record(record_file_nondupes, file_path)

    # @staticmethod
    def _write_record(self, record_file, file):

        try:
            with record_file.open("a", encoding='utf-8') as f:
                logging.debug(f'Recording info for {file} into file {record_file}')
                f.write(str(file) + "\n")
        except Exception as e:
            logging.critical(e, exc_info=True)
            logging.critical(f'Cannot write to {record_file}')

    # @staticmethod
    def _move_record_file(self, source, target):

        logging.info(f'Moving file from {source} to {target}')
        try:
            Path.rename(source, target)
        except Exception as e:
            logging.critical(e, exc_info=True)
            logging.critical(f'Cannot move file from {source} to {target}')
