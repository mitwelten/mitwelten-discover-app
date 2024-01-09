from collections.abc import Callable
from datetime import datetime
from typing import Iterable, TypeVar

from src.config.app_config import DATE_FORMAT
from src.model.deployment import Deployment

T = TypeVar('T')
def safe_reduce(fn: Callable[[T, T], T], iterable: Iterable[T], start: T|None) -> T|None:
    iterator = iter(iterable)
    accumulator = start
    for current in iterator:
        if current is None:
            continue
        if accumulator is None:
            accumulator = current
        else:
            accumulator = fn(accumulator, current)

    return accumulator


def was_deployed(deployment: Deployment, start_date: str, end_date: str):
    selected_start = datetime.strptime(start_date, DATE_FORMAT).date()
    selected_end   = datetime.strptime(end_date,   DATE_FORMAT).date()

    node_start = deployment.period_start
    node_end   = deployment.period_end

    if node_start is not None:
        node_start = datetime.strptime(node_start[0:10], DATE_FORMAT).date()
        start_in_period = selected_start <= node_start <= selected_end
        if start_in_period:
            return True
        if node_end is not None:
            node_end = datetime.strptime(node_end[0:10], DATE_FORMAT).date()
            end_in_period = selected_start <= node_end <= selected_end
            if end_in_period:
                return True
            return node_start < selected_start and node_end > selected_end
        else:
            return node_start <= selected_end

"""
INFO:
Map latitude & longitude:

          N (Latitude)
          ^
          |
 West 0---|---> (Longitude)
          |
          |
          0
          S

Map bounds format: [ bottom-left: [lat, lon], top-right [lat, lon]]
"""
def ensure_marker_visibility(
        map_center,
        map_bounds,
        marker_position,
        browser_props,
        settings_drawer_size,
        chart_drawer_size: str,
):
    marker_lat = marker_position["lat"]
    marker_lon = marker_position["lon"]

    if marker_lat is None or marker_lon is None:
        return map_center

    map_lat   = map_center[0]
    map_lon   = map_center[1]
    lower_lat = map_bounds[0][0]
    upper_lat = map_bounds[1][0]
    left_lon  = map_bounds[0][1]
    right_lon = map_bounds[1][1]

    screen_height_deg   = upper_lat - lower_lat    # latitude width of the visible map section
    screen_width_deg    = right_lon - left_lon     # longitude width of the visible map section
    screen_height_pixel = browser_props["height"]  # number of pixels of the browser window width
    screen_width_pixel  = browser_props["width"]   # number of pixels of the browser window width

    settings_drawer_percent = 100 / screen_width_pixel  * settings_drawer_size
    data_drawer_percent     = 100 / screen_height_pixel * chart_drawer_size

    target_lon = settings_drawer_percent + (100 - settings_drawer_percent) / 2
    target_lat = data_drawer_percent     + (100 - data_drawer_percent)     / 2

    center_target_lat = (screen_height_deg / 100.0 * target_lat) + lower_lat
    center_target_lon = (screen_width_deg  / 100.0 * target_lon) + left_lon

    delta_lat_move    = center_target_lat - map_lat
    delta_lon_move    = center_target_lon - map_lon

    marker_lat_normalized = marker_lat - lower_lat
    marker_lon_normalized = marker_lon - left_lon

    marker_lat_percent = (100.0 / screen_height_deg) * marker_lat_normalized
    marker_lon_percent = (100.0 / screen_width_deg) * marker_lon_normalized

    margin = 15
    borders = dict(
        top=80,
        right=80,
        bottom=data_drawer_percent + margin,
        left=settings_drawer_percent
    )

    if marker_lat_percent < borders["bottom"] or marker_lat_percent > borders["top"]:
        map_lat = marker_lat - delta_lat_move

    if marker_lon_percent < borders["right"] or marker_lon_percent > borders["left"]:
        map_lon = marker_lon - delta_lon_move

    return map_lat, map_lon
