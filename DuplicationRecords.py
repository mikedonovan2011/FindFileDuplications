import shutil
from pathlib import Path
import sys
import logging


class DuplicationRecords:

    def __init__(self, path=Path.cwd(), delete_folders_first=True):

        self.path_for_nondupes_records = path / "non_dupes"
        self.path_for_dupes_records = path / "dupes"

        self._create_folders_for_records(delete_folders_first)

    def _create_folders_for_records(self, delete_folders_first):

        if delete_folders_first:
            self._clean_up_records()

        for path in [self.path_for_nondupes_records, self.path_for_dupes_records]:
            logging.info(f'Creating folder {path} for the records.')
            try:
                Path.mkdir(path, exist_ok=True)
            except Exception as e:
                logging.critical(e, exc_info=True)
                logging.critical(f'Cannot create the folder {path}')
                sys.exit('Exiting because of critical error')

    def _clean_up_records(self):

        for folder in (self.path_for_nondupes_records, self.path_for_dupes_records):
            try:
                shutil.rmtree(folder)
                logging.info(f'Removed the folders {folder} and all contents')
            except FileNotFoundError:
                logging.info(f'No folder {folder} to remove')
            except PermissionError as e:
                logging.critical(e, exc_info=True)
                logging.critical(f'Permission issue in {folder}')
                sys.exit(f'Exiting because of permission error with {folder}')

    def add_file_information(self, file_path, file_hash):

        record_filename = file_hash + ".txt"
        record_file_dupes = self.path_for_dupes_records / record_filename
        record_file_nondupes = self.path_for_nondupes_records / record_filename

        file_needs_moving = False

        if record_file_dupes.exists():
            logging.info(f'Duplicate found; writing to: {record_file_dupes}')
            self._write_record(record_file_dupes, file_path)
        else:
            if record_file_nondupes.exists():
                file_needs_moving = True
                logging.info(f'Duplicate found; writing to: {record_file_nondupes}')
            self._write_record(record_file_nondupes, file_path)

            if file_needs_moving:
                self._move_record_file(record_file_nondupes, record_file_dupes)

    @staticmethod
    def _write_record(record_file, file):

        try:
            with record_file.open("a", encoding='utf-8') as f:
                logging.debug(f'Recording info for {file} into file {record_file}')
                f.write(str(file) + "\n")
        except Exception as e:
            logging.critical(e, exc_info=True)
            logging.critical(f'Cannot write to {record_file}')

    @staticmethod
    def _move_record_file(source, target):

        logging.info(f'Moving file from {source} to {target}')
        try:
            Path.rename(source, target)
        except Exception as e:
            logging.critical(e, exc_info=True)
            logging.critical(f'Cannot move file from {source} to {target}')
