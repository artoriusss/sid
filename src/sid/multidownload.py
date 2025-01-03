import os
import json
import time
import traceback
from tqdm import tqdm
from pathlib import Path
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

from .logger import logger
from .fetch_image import fetch_image
from .prefs import prefs


MAX_RETRIES = 50
BACKOFF_INITIAL = 2
STATE_PATH = prefs['multidownload']['entrypoint_path']


if not os.path.exists(STATE_PATH):
    raise FileNotFoundError(f"State file for multidownload not found at {STATE_PATH}.")

def load_state(file_path: str) -> Dict:
    with open(file_path, 'r') as file:
        return json.load(file)

def save_state(state: Dict, file_path: str):
    with open(file_path, 'w') as file:
        json.dump(state, file, indent=2)
    logger.debug("State saved to the disk.")

def is_item_downloaded(item: Dict) -> bool:
    return item.get('downloaded', False)

def check_state():
    img_glob = Path(prefs['images_dir']).glob('*.png')
    downloaded_images = set(img.stem for img in img_glob)
    logger.debug(f"Checking state file at {STATE_PATH}")
    logger.debug(f"Found {len(downloaded_images)} downloaded images.")

    state = load_state(STATE_PATH)
    for key, value in state.items():
        if value.get('downloaded') and key not in downloaded_images:
            logger.warning(f"Image {key} not found. Marking as not downloaded.")
            value['downloaded'] = False
    save_state(state, STATE_PATH)

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
def download_and_save_image(key: str, item: Dict):
    try:
        logger.debug(f"Starting download {key}")
        name, center_adj = fetch_image(item['lat'], item['lon'], output_key=key)
        item['status'] = 'completed'
        item['downloaded'] = True
        item['lat'] = center_adj[0]
        item['lon'] = center_adj[1]
        item['error_message'] = None
        logger.info(f"Successfully downloaded: {name}")
    except Exception as e:
        item['status'] = 'failed'
        item['error_message'] = str(e)
        logger.error(f"Failed to download image at ({item['lat']}, {item['lon']}): {e}")

def process_coordinates():
    check_state()
    state = load_state(STATE_PATH)
    n_to_process = len([item for item in state.values() if not is_item_downloaded(item)])
    logger.info(f"Found {n_to_process} items to download.")
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_key = {
            executor.submit(download_and_save_image, key, item): key
            for key, item in state.items()
            if not is_item_downloaded(item)
        }
        with tqdm(total=n_to_process) as pbar:
            for future in future_to_key:
                future.result()
                save_state(state, STATE_PATH)
                pbar.update(1)
