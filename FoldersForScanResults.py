import shutil
import logging
from pathlib import Path
from collections import namedtuple
from Configurations import Configurations


RecordFolders = namedtuple('RecordFolders', ['non_dupes_records', 'dupes_records', 'moved_dupes_records'])

class FoldersForScanResults:

    def __init__(self, configs: Configurations):

        self.configs = configs

        self.record_folders = RecordFolders(
            self.configs.location_for_scan_results / "non_dupes_records",
            self.configs.location_for_scan_results / "dupes_records",
            self.configs.location_for_scan_results / "moved_dupes_records"
        )
        self.moved_dupes_files = self.configs.location_for_moved_dupes

    def set_up_folders(self) -> None:

        if self.configs.clean_up_previous_run:
            try:
                self._clean_up_records()
            except PermissionError as e:
                logging.critical(f'Cannot clean up the folders for the records: {e}')
                raise RuntimeError('Cannot clean up the folders for the records.') from e

        try:
            self._create_folders()
        except RuntimeError as e:
            logging.critical(f'Cannot create folders for the records: {e}', exc_info=True)
            raise RuntimeError('Exiting because of critical error creating folders') from e

    def _clean_up_records(self) -> None:

        for folder in self.record_folders:
            if folder.exists():
                shutil.rmtree(folder)
                logging.info(f'Removed the folder {folder} with its contents')
            else:
                logging.info(f'No folder {folder} to remove')

    def _create_folders(self):

        for path in (*self.record_folders, self.moved_dupes_files):
            Path.mkdir(path, exist_ok=True, parents=True)
            if not path.exists():
                logging.critical(f'Cannot create the folder {path}')
                raise RuntimeError('Cannot create the folder for scan results')

    @property
    def record_folder_paths(self) -> RecordFolders:
        return self.record_folders

    @property
    def moved_dupes_files_path(self) -> Path:
        return self.moved_dupes_files
