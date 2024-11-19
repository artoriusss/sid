import os
import json
import re
import cv2
from datetime import datetime

from .prefs import file_dir, prefs_path
from .image_downloading import download_image
from .adjust_resolution import adjust_for_resolution

def take_input(messages: list) -> list:
    inputs = []
    print('Enter "r" to reset or "q" to exit.')
    for message in messages:
        inp = input(message)
        if inp == 'q' or inp == 'Q':
            return None
        if inp == 'r' or inp == 'R':
            return take_input(messages)
        inputs.append(inp)
    return inputs

def run():
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    if (prefs['tl'] == '') or (prefs['br'] == '') or (prefs['zoom'] == ''):
        messages = ['Center point (lat, lon): ', 'Zoom level: ']
        inputs = take_input(messages)
        if inputs is None:
            return
        else:
            prefs['tl'], prefs['zoom'] = inputs

    center_lat, center_lon = re.findall(r'[+-]?\d*\.\d+|d+', prefs['tl'])

    zoom = int(prefs['zoom'])
    channels = int(prefs['channels'])
    tile_size = int(prefs['tile_size'])
    center_lat = float(center_lat)
    center_lon = float(center_lon)

    top_left, bottom_right = adjust_for_resolution(center_lat, center_lon, zoom)
    lat1, lon1 = top_left
    lat2, lon2 = bottom_right
    img = download_image(lat1, lon1, lat2, lon2, zoom, prefs['url'],
        prefs['headers'], tile_size, channels)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    cv2.imwrite(os.path.join(prefs['dir'], name), img)
    print(f'Saved as {name}')

if os.path.isfile(prefs_path):
    run()