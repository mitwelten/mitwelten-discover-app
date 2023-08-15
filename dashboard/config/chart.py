from functools import partial

from dashboard.components.data_drawer.types.audio import create_audio_chart
from dashboard.components.data_drawer.types.env import create_env_chart
from dashboard.components.data_drawer.types.environment import create_environment_chart
from dashboard.components.data_drawer.types.pax import create_pax_chart
from dashboard.components.data_drawer.types.pollinator import create_pollinator_chart


def get_supported_chart_types(legend=None):
    return {
        "Env. Sensor": create_env_chart,
        "Pax Counter": create_pax_chart,
        "Audio Logger": create_audio_chart,
        "Pollinator Cam": create_pollinator_chart,
        "Environment": partial(create_environment_chart, legend)
    }

