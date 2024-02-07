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

# def plot_image(image):
#     buffered = BytesIO()
#     image.save(buffered, format="PNG")
#     img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
#     return html.Img(id="my-img", className="image", src="data:image/png;base64, " + img_str)
