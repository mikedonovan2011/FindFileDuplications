import shutil
from pathlib import Path
import sys
import logging
from collections import namedtuple

Folders = namedtuple('Folders', ['non_dupes', 'dupes'])

class FoldersForOutput:
    def __init__(self, path=Path.cwd(), delete_folders_previous_run: bool = True):

        self.folders = Folders(path / "non_dupes", path / "dupes")  
        self.delete_folders_previous_run= delete_folders_previous_run

        self._create_folders()

    def _create_folders(self):

        if self.delete_folders_previous_run:
            if not self._clean_up_records():
                raise Exception('Cannot clean up the folders for the records.')

        for path in (self.folders):
            logging.info(f'Creating folder {path} for the records.')
            try:
                Path.mkdir(path, exist_ok=True)
            except Exception as e:
                logging.critical(e, exc_info=True)
                logging.critical(f'Cannot create the folder {path}')
                sys.exit('Exiting because of critical error')
            
    def _clean_up_records(self):

        for folder in (self.folders):
            if not folder.exists():
                logging.info(f'No folder {folder} to remove')
                continue
            try:
                shutil.rmtree(folder)
                logging.info(f'Removed the folder {folder} with its contents')               
            except PermissionError as e:
                logging.critical(e, exc_info=True)
                logging.critical(f'Could not remove the folder {folder} with its contents')
                return False
            return True

    @property
    def folder_paths(self) -> Folders:
        return self.folders  
