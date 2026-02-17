import sys
import logging
from Configurations import Configurations
from DuplicationRecords import DuplicationRecords
from FoldersForScanResults import FoldersForScanResults

def main():

    logging.basicConfig(filename='file_dupes.log', filemode='w', format='%(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)
    try:
        configs = Configurations()
    except RuntimeError as e:
        logging.critical(e, exc_info=True)
        sys.exit(f'Exiting because of critical error reading config: {e}')

    folders_this_run = FoldersForScanResults(configs)
    try:
        folders_this_run.set_up_folders()
    except RuntimeError as e:
        logging.critical(e, exc_info=True)
        sys.exit(f'Exiting because of critical error setting up folders: {e}')

    duplication_records = DuplicationRecords(folders_this_run, configs)

    try:
        for folder in configs.folders_to_scan:
            logging.info(f'Analyzing folder: {folder}')
            duplication_records.analyze_folder(folder)
            logging.info(f'Finished analyzing folder: {folder}')
    except RuntimeError as e:
        logging.critical(e, exc_info=True)
        sys.exit(f'Exiting because of critical error during scan: {e}')

    logging.info('All done')

if __name__ == '__main__':
    
    main()
    