import os
import json

def get_user_preferences():
    """
    Prompt the user to enter the desired zoom level, image width, and image height,
    or use the default values.
    Returns:
        dict: A dictionary containing the user preferences.
    """
    default_values = {
        'zoom': {'name': 'zoom level', 'value': 19},
        'width': {'name': 'image width', 'value': 4000},
        'height': {'name': 'image height', 'value': 3000},
    }
    preferences = {}
    for key, default in default_values.items():
        while True:
            user_input = input(f"Enter the desired {default['name']} or 'd' for default ({default['value']}): ").strip().lower()
            if user_input in ('d', ''):
                preferences[key] = default['value']
                break
            try:
                value = int(user_input)
                if value > 0:
                    preferences[key] = value
                    break
                else:
                    print(f"{key.capitalize()} must be a positive integer.")
            except ValueError:
                print(f"Invalid input. Please enter a valid integer for {key} or 'd' for default.")
    return preferences

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

# Default preferences template
prefs = {
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
        'user-agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
        )
    },
    'tl': '',
    'br': '',
    'width': '',
    'height': '',
    'zoom': '',
}

if not os.path.isfile(prefs_path):
    try:
        print("Configuring preferences file...")
        user_prefs = get_user_preferences()
        prefs.update(user_prefs)
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
        print(f'Preferences file created at {prefs_path}')
    except IOError as e:
        print(f"Error writing preferences file {prefs_path}: {e}")
        raise

with open(prefs_path, 'r', encoding='utf-8') as f:
    prefs = json.load(f)