from functools import partial

from dashboard.components.data_drawer.types.audio import create_audio_chart
from dashboard.components.data_drawer.types.env import create_env_chart
from dashboard.components.data_drawer.types.environment_point import create_environment_point_chart
from dashboard.components.data_drawer.types.note import create_note_form
from dashboard.components.data_drawer.types.pax import create_pax_chart
from dashboard.components.data_drawer.types.pollinator import create_pollinator_chart


def get_display_supported_types(legend=None):
    return {
        "Env. Sensor": create_env_chart,
        "Pax Counter": create_pax_chart,
        "Audio Logger": create_audio_chart,
        "Pollinator Cam": create_pollinator_chart,
        "Environment": partial(create_environment_point_chart, legend),
        "Note": create_note_form
    }

