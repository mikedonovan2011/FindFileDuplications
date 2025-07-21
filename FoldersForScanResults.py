import shutil
from pathlib import Path
import sys
import logging
from collections import namedtuple
from Configurations import Configurations


Folders = namedtuple('Folders', ['non_dupes', 'dupes'])

class FoldersForScanResults:

    def __init__(self, configs: Configurations):

        self.configs = configs

        self.folders = Folders(self.configs.location_for_scan_results / "non_dupes", 
                               self.configs.location_for_scan_results / "dupes")  
        
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

        for folder in self.folders:
            if folder.exists():
                try:
                    shutil.rmtree(folder)
                    logging.info(f'Removed the folder {folder} with its contents')               
                except PermissionError as e:
                    logging.critical(f'Could not remove the folder {folder} with its contents: {e}', 
                                    exc_info=True)
            else:
                logging.info(f'No folder {folder} to remove')

    def _create_folders(self):
         
        for path in self.folders:
            logging.info(f'Creating folder {path} for the records.')
            print(path)
            try:
                Path.mkdir(path, exist_ok=True, parents=True)
            except Exception as e:
                logging.critical(f'Cannot create the folder {path}')
                raise RuntimeError('Cannot create the folder for scan results') from e
            
    
    @property
    def folder_paths(self) -> Folders:
        return self.folders  
