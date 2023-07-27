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
