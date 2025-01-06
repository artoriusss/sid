import time
import traceback
from tqdm import tqdm
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

from ..utils.logger import logger
from ..fetch_image import fetch_image
from .StateManager import StateManager
from .constants import MAX_RETRIES, BACKOFF_INITIAL, MAX_WORKERS


def retry_on_failure(max_retries: int = MAX_RETRIES, initial_backoff: int = BACKOFF_INITIAL):
    def decorator(func):
        def wrapper(*args, **kwargs):
            backoff_time = initial_backoff
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error: {e}, Traceback: {traceback.format_exc()}")
                    time.sleep(backoff_time)
                    backoff_time *= 2
                    logger.debug(f"Retrying... Attempt {attempt + 1}")
                    if attempt == max_retries - 1:
                        logger.error("Max retries reached. Moving to next item.")
        return wrapper
    return decorator

@retry_on_failure()
def download_and_save_image(sm: StateManager, key: str, item: Dict):
    provider_key = None
    try:
        logger.debug(f"Starting download {key}")
        provider_key = key.split('_')[-1]
        name, (lat, lon) = fetch_image(item['lat'], item['lon'], output_key=key, provider_key=provider_key)
        sm.update_item_status(key, lat=lat, lon=lon, status='completed', downloaded=True)
        logger.debug(f"Successfully downloaded: {name}")
    except Exception as e:
        item['status'] = 'failed'
        item['error_message'] = str(e)
        logger.error(f"Failed to download image for provider ({provider_key}): {e}")

def fetch_images():
    with StateManager() as sm:
        state = sm.get_state()
        n_to_process = len([item for item in state.values() if not sm.is_item_downloaded(item)])
        logger.info(f"Found {n_to_process} items to download.")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_key = {
                executor.submit(download_and_save_image, sm, key, item): key
                for key, item in state.items()
                if not sm.is_item_downloaded(item)
            }
            with tqdm(total=n_to_process) as pbar:
                for future in future_to_key:
                    future.result()
                    pbar.update(1)
