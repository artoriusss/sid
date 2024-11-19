import os
import cv2
from datetime import datetime
from typing import Dict

from .image_downloading import download_image
from .adjust_resolution import adjust_for_resolution

def fetch_image(center_lat: float, center_lon: float, prefs: Dict) -> None:
    """
    Fetches an image from the specified center point.

    Args:
        center_lat (float): The latitude of the center point.
        center_lon (float): The longitude of the center point.
        prefs (dict): The preferences for the image.

    Returns:
        None
    """
    top_left, bottom_right = adjust_for_resolution(center_lat, center_lon, prefs['zoom'])
    lat1, lon1 = top_left
    lat2, lon2 = bottom_right
    img = download_image(lat1, lon1, lat2, lon2, prefs['zoom'], prefs['url'],
        prefs['headers'], prefs['tile_size'], prefs['channels'])
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    cv2.imwrite(os.path.join(prefs['dir'], name), img)
    print(f'Saved as {name}')