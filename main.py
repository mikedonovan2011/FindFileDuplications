from pathlib import Path
import hashlib
import logging
import sys
from Configurations import Configurations
from DuplicationRecords import DuplicationRecords


def main(*root_folders):

    logging.basicConfig(filename='file_dupes.log', filemode='w', format='%(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.INFO)
    
    config_file = Path.cwd() / 'config.ini'
    configs = Configurations(config_file)

    duplication_records = DuplicationRecords(delete_folders_first=configs.clean_up)

    for folder in root_folders:
        if not Path(folder).is_dir():
            logging.warning(f'{folder} does not exist')
            continue
        logging.info(f'Looking at files in {folder}')
        file_paths = Path(folder).glob("**/*")  # gives a generator with all sub-folders and files

        for path in file_paths:
            if skip_file(path, configs):
                continue
            try:
                with path.open("rb") as file_handle:
                    file_hash = hashlib.file_digest(file_handle, "md5").hexdigest()
                    duplication_records.add_file_information(path, file_hash)
            except PermissionError as e:
                logging.critical(e, exc_info=True)
                logging.critical(f'Cannot access {path}')
                sys.exit(f'Exiting because of permission error with {path}')

    logging.info('All done')


def skip_file(filepath, configs):
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