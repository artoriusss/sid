from pathlib import Path
from typing import Dict, Any

from ..utils.logger import logger
from ..utils.prefs import prefs
from .constants import ENTRYPOINT_PATH, STATE_PATH, PROVIDERS
from .FileManager import FileManager

class StateManager():
    def __init__(self):
        self._prepare_state()

    def __str__(self) -> str:
        return str(self.state)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.save_state()
        except Exception as save_exception:
            logger.error(f"Failed to save state: {save_exception}")
        return False

    def _prepare_state(self):
        try:
            self.state = self.load_state()
            self.check_state()
            logger.debug(f"State loaded successfully from {STATE_PATH}.")
        except FileNotFoundError:
            logger.debug(f"State file not found at {STATE_PATH}. Creating a new initial state.")
            self._create_new_state()

    def _create_new_state(self):
        self.state = {}
        try:
            entrypoint_data = FileManager.read_json(ENTRYPOINT_PATH)
            for key, item in entrypoint_data.items():
                for provider_key in PROVIDERS.keys():
                    self._add_new_key(key, item, provider_key)
            self.save_state()
        except FileNotFoundError:
            raise FileNotFoundError(f"Attemped to create state file, but entrypoint file not found at {ENTRYPOINT_PATH}.")

    def _add_new_key(self, key, item, provider_key: str):
        self.state[f"{key}_{provider_key}"] = {
            'lat': item['lat'],
            'lon': item['lon'],
            'status': 'pending',
            'downloaded': False,
            'error_message': None
        }

    def check_state(self):
        self._check_providers()
        self._check_downloads()
        self.save_state()

    def _check_downloads(self):
        img_glob = Path(prefs['images_dir']).glob('*.png')
        downloaded_images = set(img.stem for img in img_glob)
        logger.debug(f"Checking state file at {STATE_PATH}")
        logger.debug(f"Found {len(downloaded_images)} downloaded images.")

        state = self.load_state()
        for key, value in state.items():
            if value.get('downloaded') and key not in downloaded_images:
                logger.warning(f"Image {key} not found. Marking as not downloaded.")
                self.update_item_status(key, downloaded=False)

    def _check_providers(self):
        try:
            current_providers = set(PROVIDERS.keys())
            entrypoint_data = FileManager.read_json(ENTRYPOINT_PATH)
            keys_to_delete = set()
            added_providers = {key.split('_')[-1] for key in self.state.keys()}

            for key in list(self.state.keys()):
                provider_key = key.split('_')[-1]
                if provider_key not in current_providers:
                    logger.warning(f"Provider {provider_key} not found in providers. Marking for removal.")
                    keys_to_delete.add(key)

            # Remove marked keys
            for key in keys_to_delete:
                del self.state[key]

            # Add new providers
            new_providers = current_providers - added_providers
            logger.warning(f"New providers found in preferences: {new_providers}")
            if new_providers:
                for entry_key, item in entrypoint_data.items():
                    for provider_key in new_providers:
                        self._add_new_key(entry_key, item, provider_key)

        except FileNotFoundError:
            logger.warning(f"Entrypoint file not found at {ENTRYPOINT_PATH}. Cannot check providers.")

    def get_state(self) -> Dict:
        return self.state

    def is_item_downloaded(self, item: Dict) -> bool:
        return item.get('downloaded', False)

    def load_state(self) -> Dict:
        return FileManager.read_json(STATE_PATH)

    def save_state(self):
        FileManager.write_json(STATE_PATH, self.state)

    def update_item_status(self, key: str, **kwargs: Any) -> None:
        if key in self.state:
            allowed_keys = {'lat', 'lon', 'status', 'downloaded', 'error_message'}
            updates = {k: v for k, v in kwargs.items() if k in allowed_keys}
            if updates:
                self.state[key].update(updates)
                logger.debug(f"Updated state for {key}: {updates}")
            else:
                logger.debug(f"No valid updates for {key}.")
