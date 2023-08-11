from collections.abc import Callable
from datetime import datetime
from typing import Iterable, TypeVar

from dashboard.model.deployment import Deployment

T = TypeVar('T')


def safe_reduce(fn: Callable[[T, T], T], iterable: Iterable[T], start: T = None) -> int:
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
    selected_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    selected_end = datetime.strptime(end_date, "%Y-%m-%d").date()

    node_start = deployment.period_start
    node_end = deployment.period_end

    if node_start is not None:
        node_start = datetime.strptime(node_start[0:10], "%Y-%m-%d").date()
        start_in_period = selected_start <= node_start <= selected_end
        if start_in_period:
            return True
        if node_end is not None:
            node_end = datetime.strptime(node_end[0:10], "%Y-%m-%d").date()
            end_in_period = selected_start <= node_end <= selected_end
            if end_in_period:
                return True
            return node_start < selected_start and node_end > selected_end
        else:
            return node_start <= selected_end


def ensure_marker_visibility(map_center, map_bounds, marker_position, target_horizontal=60, target_vertical=75):
    map_lat = map_center[0]
    map_lon = map_center[1]
    marker_lat = marker_position["lat"]
    marker_lon = marker_position["lon"]
    lower_lat = map_bounds[0][0]
    upper_lat = map_bounds[1][0]
    left_lon = map_bounds[0][1]
    right_lon = map_bounds[1][1]

    # lat
    screen_height = upper_lat - lower_lat
    marker_lat_normalized = marker_lat - lower_lat
    percentage_marker_lat_on_screen = (100.0 / screen_height) * marker_lat_normalized
    center_target_lat = ((screen_height / 100.0) * target_vertical) + lower_lat
    delta_lat_move = center_target_lat - map_lat

    # lon
    screen_width = right_lon - left_lon
    marker_lon_normalized = marker_lon - left_lon
    percentage_marker_lon_on_screen = (100.0 / screen_width) * marker_lon_normalized
    center_target_lon = ((screen_width / 100.0) * target_horizontal) + left_lon
    delta_lon_move = center_target_lon - map_lon

    if percentage_marker_lat_on_screen < 60:
        map_lat = marker_lat - delta_lat_move # 46 - 2.5 = 43.5

    if percentage_marker_lon_on_screen < 20:
        map_lon = marker_lon - delta_lon_move

    return map_lat, map_lon
