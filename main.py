from pathlib import Path
import logging
from Configurations import Configurations
from DuplicationRecords import DuplicationRecords
from FoldersForOutput import FoldersForOutput
import sys

def main(*root_folders):

    logging.basicConfig(filename='file_dupes.log', filemode='w', format='%(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.INFO)
    
    config_file = Path.cwd() / 'config.iniW'
    try:
        configs = Configurations(config_file)
    except Exception as e:
        logging.critical(e, exc_info=True)
        sys.exit(f'Exiting because of critical error reading config: {e}')

    folders_this_run = FoldersForOutput(delete_folders_previous_run=configs.clean_up)
    duplication_records = DuplicationRecords(folders_this_run.folder_paths)

    for folder in root_folders:
        if not Path(folder).is_dir():
            logging.warning(f'{folder} does not exist')
            continue
        logging.info(f'Looking at files in {folder}')
        file_paths = Path(folder).glob("**/*")  # gives a generator with all sub-folders and files

        for path in file_paths:
            if not skip_file(path, configs):
                duplication_records.analyze_file(path)

    logging.info('All done')


def skip_file(filepath: Path, configs: Configurations):
    if filepath.suffix not in configs.supported_file_types:
        return True
    if filepath.stat().st_size > configs.max_file_size:
        logging.info(f'Skipping file {filepath} because its size is > {configs.max_file_size}')
        return True
    if filepath.stat().st_size < configs.min_file_size:
        logging.info(f'Skipping file {filepath} because its size is < {configs.min_file_size}')
        return True
    return False


if __name__ == '__main__':
    main("tests\\test_files")