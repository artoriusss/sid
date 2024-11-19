import os
import json

project_dir = os.getcwd()
config_dir = os.path.join(project_dir, '.config')
prefs_path = os.path.join(config_dir, 'sid_preferences.json')
image_dir = os.path.join(project_dir, 'sid_images')

for directory in [config_dir, image_dir]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            raise

default_prefs = {
    'url': 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    'tile_size': 256,
    'channels': 3,
    'dir': image_dir,
    'headers': {
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    },
    'tl': '',
    'br': '',
    'zoom': 21
}

if not os.path.isfile(prefs_path):
    try:
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(default_prefs, f, indent=2, ensure_ascii=False)
        print(f'Preferences file created in {prefs_path}')
    except IOError as e:
        print(f"Error writing preferences file {prefs_path}: {e}")
        raise