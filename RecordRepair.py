import logging
from pathlib import Path


class RecordRepair:

    def __init__(self, paths):

        self.path_for_records = paths

    def repair(self) -> None:

        logging.info('Checking non_dupes records for inconsistencies')
        for record_file in self.path_for_records.non_dupes.glob("*.txt"):
            with record_file.open("r", encoding='utf-8') as f:
                line_count = sum(1 for line in f if line.strip())

            if line_count == 0:
                logging.info(f'Deleting empty record: {record_file.name}')
                self._delete_record(record_file)
            elif line_count >= 2:
                target = self.path_for_records.dupes / record_file.name
                logging.info(f'Repairing: {record_file.name} has {line_count} paths, moving to dupes')
                self._move_record_file(record_file, target)

        logging.info('Checking deleted_dupes records for inconsistencies')
        for record_file in self.path_for_records.deleted_dupes.glob("*.txt"):
            with record_file.open("r", encoding='utf-8') as f:
                line_count = sum(1 for line in f if line.strip())

            if line_count == 0:
                logging.info(f'Deleting empty deleted_dupes record: {record_file.name}')
                self._delete_record(record_file)

    @staticmethod
    def _delete_record(record_file: Path):

        try:
            record_file.unlink()
        except Exception as e:
            logging.critical(f'Cannot delete {record_file}: {e}', exc_info=True)
            raise RuntimeError(f'Cannot delete {record_file}: {e}') from e

    @staticmethod
    def _move_record_file(source: Path, target: Path):

        logging.info(f'Moving file from {source} to {target}')
        try:
            Path.rename(source, target)
        except Exception as e:
            logging.critical(f'Cannot move file from {source} to {target}: {e}', exc_info=True)
            raise RuntimeError(f'Cannot move file from {source} to {target}') from e
