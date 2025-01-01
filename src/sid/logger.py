import logging
import json

from .prefs import prefs_path

DEFAULT_LOGGING_LEVEL = 'WARNING'

with open(prefs_path, 'r') as config_file:
    config = json.load(config_file)

log_level_str = config.get('logging_level', DEFAULT_LOGGING_LEVEL)
log_level = getattr(logging, log_level_str.upper(), logging.WARNING)

logger = logging.getLogger('SID_logger')
logger.setLevel(log_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
