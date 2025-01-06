import os
import subprocess
from datetime import datetime
import yaml

from .prefs import apikeys_path
from .logger import logger


def load_api_keys(file_path=apikeys_path):
    """
    Load API keys from a YAML file.

    :param file_path: Path to the YAML file containing API keys.
    :return: Dictionary of API keys.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The API key file '{file_path}' could not be found.")
    with open(file_path, 'r') as f:
        api_keys = yaml.safe_load(f)
    return api_keys

def should_update_key(last_timestamp_unix):
    now_unix = int(datetime.utcnow().timestamp())
    logger.debug(f"Current time: {now_unix}, last update time: {last_timestamp_unix}, difference: {now_unix - last_timestamp_unix}")
    return abs(now_unix - last_timestamp_unix) > 60

def prepare_apple_apikey():
    api_keys = load_api_keys()
    if 'AM' in api_keys and 'timestamp' in api_keys['AM']:
        last_timestamp = api_keys['AM']['timestamp']
        if not should_update_key(last_timestamp):
            logger.debug("API key is recent; no update needed.")
            return

    try:
        logger.info("Updating Apple API key...")
        script_path = os.path.join(os.path.dirname(__file__), 'updateAppleToken.js')
        subprocess.run(["node", script_path], check=True)
        print("JavaScript script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the JavaScript file: {e}")

def prepare_url(raw_url: str, provider_key: str) -> str:
    """
    Append an API key to the URL if available.

    :param raw_url: The base URL to which the API key is appended.
    :param provider_key: The key to identify which API provider's key to use.
    :return: The formatted URL with the API key appended if available.
    """
    prepare_apple_apikey()
    api_keys = load_api_keys()
    if provider_key in api_keys:
        url = raw_url + api_keys[provider_key]['key']
    else:
        url = raw_url
    logger.debug(f"Prepared URL: {url}")
    return url
