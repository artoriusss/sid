from ..utils.prefs import prefs

ENTRYPOINT_PATH = prefs['multidownload']['entrypoint_path']
STATE_PATH = prefs['multidownload']['state_path']

PROVIDERS = prefs['providers']
MAX_RETRIES = 50
BACKOFF_INITIAL = 2
MAX_WORKERS = prefs['multidownload']['concurrent_workers']
