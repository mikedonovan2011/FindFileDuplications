from pathlib import Path
import logging
from Configurations import Configurations
from DuplicationRecords import DuplicationRecords
from FoldersForScanResults import FoldersForScanResults
import sys

def main():

    logging.basicConfig(filename='file_dupes.log', filemode='w', format='%(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)
    
    try:
        configs = Configurations()
    except Exception as e:
        logging.critical(e, exc_info=True)
        sys.exit(f'Exiting because of critical error reading config: {e}')

    folders_this_run = FoldersForScanResults(configs)
    folders_this_run.set_up_folders()
    duplication_records = DuplicationRecords(folders_this_run.folder_paths)

    folders_to_scan = configs.folders_to_scan

    for folder in folders_to_scan:
        if folder.is_dir() is False:
            logging.warning(f'{folder} does not exist')
            continue
        logging.info(f'Looking at files in {folder}')
        file_paths = folder.glob("**/*")  # gives a generator with all sub-folders and files

        for path in file_paths:
            if not skip_file(path, configs):
                duplication_records.analyze_file(path)

    logging.info('All done')


def skip_file(filepath: Path, configs: Configurations):
    if filepath.suffix not in configs.supported_file_types:
        logging.debug(f'Skipping file {filepath} because its type is not supported')
        return True
    
    file_size = filepath.stat().st_size
    if configs.min_file_size <= file_size <= configs.max_file_size:
        return False
    logging.info(f'Skipping file {filepath} because its size is {file_size}')
    return True



if __name__ == '__main__':
    
    main()
    