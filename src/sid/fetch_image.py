import os
import cv2
from datetime import datetime
from typing import Tuple

from .utils import logger, prefs, adjust_for_resolution, prepare_url, download_image


def fetch_image(
        center_lat: float,
        center_lon: float,
        width: int = prefs['width'],
        height: int = prefs['height'],
        output_key: str = "",
        provider_key: str = "GM"
        ) -> Tuple[str, Tuple[float, float]]:
    """Fetches an image from the specified center point.

        :param center_lat: latitude of the center point.
        :param center_lon: longitude of the center point.
        :param zoom: zoom level of the image (if not specified, the default from preferences file is used).
        :param width: width of the image.
        :param height: height of the image.

        :return: name of the image file and adjusted center coordinates.
    """
    raw_url = prefs['providers'][provider_key]['url']
    url = prepare_url(raw_url, provider_key)
    zoom = prefs['providers'][provider_key]['zoom']
    tile_size = prefs['providers'][provider_key]['tile_size']
    top_left, bottom_right, center_adj  = adjust_for_resolution(center_lat, center_lon, zoom, width, height)
    lat1, lon1 = top_left
    lat2, lon2 = bottom_right
    img = download_image(
                        lat1, lon1, lat2, lon2,
                        zoom,
                        url,
                        prefs['headers'],
                        tile_size=tile_size,
                        channels=prefs['channels']
    )

    if output_key:
        cv2.imwrite(os.path.join(prefs['images_dir'], f"{output_key}.png"), img)
        logger.debug(f'Saved as {output_key}.png')
        return output_key, center_adj
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    cv2.imwrite(os.path.join(prefs['images_dir'], name), img)
    logger.debug(f'Saved as {name}')
    return name, center_adj
