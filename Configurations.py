import configparser
import logging


class Configurations:

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not self.config_file.exists():
            raise FileNotFoundError(f'configuration file {self.config_file} not found')
        self._load_config()

        
    def _load_config(self):
        try:
            self.config.read(self.config_file)
            logging.info(f'Configuration file {self.config_file} loaded successfully.') 
        except (OSError, configparser.ParsingError) as e:
            logging.error(f'***Failed to load configuration file {self.config_file}: {e}')
            raise RuntimeError(f'Configuration file {self.config_file} not readable') from e

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
        return file_types.split(',')
    
    @property
    def clean_up(self) -> bool:
        return self.config['clean_up_previous_run'].getboolean('clean_up', True) 