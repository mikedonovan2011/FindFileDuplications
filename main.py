from pathlib import Path
import hashlib
import logging
import sys
from DuplicationRecords import DuplicationRecords


def main(*root_folders):
    max_file_size = 1073741824  # files larger than 1G will be ignored 1024*1024*1024
    min_file_size = 10240 # files smaller than 10k might be thumbnails

    logging.basicConfig(filename='file_dupes.log', filemode='w', format='%(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.INFO)

    duplication_records = DuplicationRecords(delete_folders_first=True)

    for folder in root_folders:
        if not Path(folder).is_dir():
            logging.warning(f'{folder} does not exist')
            print(f'{folder} does not exist')
            continue
        logging.info(f'Looking at files in {folder}')
        file_paths = Path(folder).glob("**/*")  # gives a generator with all sub-folders and files

        for path in file_paths:
            if path.suffix not in [".jpg", ".JPG", ".JPEG", ".jpeg", ".bmp", ".BMP", ".png", ".PNG"]:
                continue
            # if not path.is_file():
            #     continue
            # if path.stat().st_size > max_file_size:
            #     logging.info(f'Skipping file {path} because its size is > {max_file_size}')
            #     continue
            if path.stat().st_size < min_file_size:
                logging.info(f'Skipping file {path} because its size is < {min_file_size}')
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


if __name__ == '__main__':
    main("test_files\\folder1", "test_files\\folder2")