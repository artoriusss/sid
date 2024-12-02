import math
from typing import Tuple

from .image_downloading import image_size

def calculate_image_coords(
        lat: float,
        lon: float,
        w: int,
        h: int,
        z: int
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Calculate the coordinates of the top left and bottom right corners of an image.

    :param lat: The latitude of the center point.
    :param lon: The longitude of the center point.
    :param w: The width of the image.
    :param h: The height of the image.
    :param z: The zoom level of the image.

    :return: The coordinates of the top left and bottom right corners of the image.
    """
    R = (256 * 2**z) / 360
    delta_lon, delta_lat = w / R, h / R

    top_left =  lat + (delta_lat / 2), lon - (delta_lon / 2)
    bottom_right = lat - (delta_lat / 2), lon + (delta_lon / 2)

    return top_left, bottom_right

def center(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    return (lat1 + lat2) / 2, (lon1 + lon2) / 2

def distance(
        origin: Tuple[float, float],
        destination: Tuple[float, float]
        ) -> float:
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d

def adjust_coords(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        zoom: int,
        desired_width: int = 4000,
        desired_height: int = 3000,
        print_info: bool = False
    ) -> Tuple[float, float, float, float, Tuple[float, float]]:
    """Adjust the coordinates of the image to match the desired resolution.

    :param lat1: The latitude of the top left corner.
    :param lon1: The longitude of the top left corner.
    :param lat2: The latitude of the bottom right corner.
    :param lon2: The longitude of the bottom right corner.
    :param zoom: The zoom level of the image.
    :param desired_width: The desired width of the image.
    :param desired_height: The desired height of the image.
    :param print_info: Whether to print information about the adjustment.

    :return: The adjusted coordinates of the image.
    """
    init_center = center(lat1, lon1, lat2, lon2)
    tolerance = 0.1
    adjustment_step = 0.001
    cnt = 0
    max_iterations = 10**5

    while cnt < max_iterations:
        width, height = image_size(lat1, lon1, lat2, lon2, zoom)

        if abs(width - desired_width) < tolerance and abs(height - desired_height) < tolerance:
            break

        if height < desired_height:
            lat1 = min(lat1 + adjustment_step, 90)
        else:
            lat1 = max(lat1 - adjustment_step, -90)

        if width < desired_width:
            lon2 = min(lon2 + adjustment_step, 180)
        else:
            lon2 = max(lon2 - adjustment_step, -180)

        cnt += 1
        adjustment_step = max(0.00001, adjustment_step * 0.99)

        if width > 10 * desired_width or height > 10 * desired_height:
            print("Dimension explosion detected. Aborting adjustments.")
            break

    adjusted_center = center(lat1, lon1, lat2, lon2)
    delta = distance(init_center, adjusted_center)
    if print_info:
        print(f"Center distorted by {delta:.2f} km due to resolution adjustment.")

    return lat1, lon1, lat2, lon2, adjusted_center

def adjust_for_resolution(
        center_lat: float,
        center_lon: float,
        zoom: int,
        width: int,
        height: int
        ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    """Adjust the coordinates of the image to match the desired resolution.

    :param center_lat: The latitude of the center point.
    :param center_lon: The longitude of the center point.
    :param zoom: The zoom level of the image.
    :param width: The width of the image.
    :param height: The height of the image.

    :return: The adjusted coordinates of the image.
    """
    (lat1, lon1), (lat2, lon2) = calculate_image_coords(center_lat, center_lon, width, height, zoom)
    lat1, lon1, lat2, lon2, _ = adjust_coords(lat1, lon1, lat2, lon2, zoom, width, height)
    lat1, lon1, lat2, lon2, center_adj = adjust_coords(lat1, lon1, lat2, lon2, zoom, width, height)
    top_left = lat1, lon1
    bottom_right = lat2, lon2
    return top_left, bottom_right, center_adj
