import logging
import configparser
from pathlib import Path


class Configurations:

    def __init__(self):

        self.config_file = Path(__file__).resolve().parent / 'config.ini'

        if not self.config_file.exists():
            message = f'Configuration file {self.config_file} not found.'
            logging.critical(message)
            raise RuntimeError(message)
        
        self.config = configparser.ConfigParser()
        self._load_config()
        self._validate_file_sizes()

    def _load_config(self):
        try:
            self.config.read(self.config_file)
            logging.info(f'Configuration file {self.config_file} loaded successfully.') 
        except (OSError, configparser.ParsingError) as e:
            logging.critical(f'Failed to load configuration file {self.config_file}: {e}')
            raise RuntimeError(f'Configuration file {self.config_file} not readable') from e

    def _validate_file_sizes(self):
        if self.min_file_size < 0:
            message = f'min_file_size cannot be negative: {self.min_file_size}'
            logging.critical(message, exc_info=True)
            raise RuntimeError(message)
        if self.max_file_size < 0:
            message = f'max_file_size cannot be negative: {self.max_file_size}'
            logging.critical(message, exc_info=True)
            raise RuntimeError(message)
        if self.min_file_size >= self.max_file_size:
            message = f'min_file_size ({self.min_file_size}) must be less than max_file_size ({self.max_file_size})'
            logging.critical(message, exc_info=True)
            raise RuntimeError(message)

    @property
    def max_file_size(self) -> int:
        return self.config['file_sizes'].getint('max_file_size', 1073741824)  # 1 GiB
    
    @property
    def min_file_size(self) -> int:
        return self.config['file_sizes'].getint('min_file_size', 0)
    
    @property
    def supported_file_types(self) -> list[str]:
        file_types = self.config['supported_files'].get('file_extensions', \
                                ".jpg,.JPG,.jpeg,.JPEG,.bmp,.BMP,.png,.PNG")
        return [ft.strip() for ft in file_types.split(',')]
    
    @property
    def clean_up_previous_run(self) -> bool:
        return self.config['clean_up_previous_run'].getboolean('clean_up', True) 
    
    @property
    def delete_duplicate_file(self) -> bool:
        return self.config['delete_duplicate_file'].getboolean('delete', False)
    
    @property
    def folders_to_scan(self) -> list[Path]:
        folders_to_scan = self.config['folders_to_scan'].get('folders', '').split(',')
        return [Path(folder.strip()).resolve() for folder in folders_to_scan if folder.strip()]

    @property
    def location_for_scan_results(self) -> Path:
        location = self.config['location_for_scan_results'].get('location', 'scan_results')
        return Path(location).resolve()
        