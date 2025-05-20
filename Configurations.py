import configparser
import logging
import sys

class Configurations:

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
        
        
    def load_config(self):
        if not self.config.read(self.config_file):
            logging.critical(f'Configuration file {self.config_file} not found. Exiting')
            sys.exit('Exiting because of critical error')
        logging.info(f'Configuration file {self.config_file} loaded successfully.') 

    @property
    def max_file_size(self):
        return int(self.config['file_sizes']['max_file_size'])
    
    @property
    def min_file_size(self):
        return int(self.config['file_sizes']['min_file_size'])  
    
    @property
    def supported_file_types(self):
        file_types = self.config['supported_files']['file_extensions']
        return file_types.split(',')
    
    @property
    def clean_up(self):
        return self.config['clean_up_previous_run'].getboolean('clean_up', True) 