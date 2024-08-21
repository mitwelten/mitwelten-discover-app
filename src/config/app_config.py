DATA_SOURCES_WITHOUT_CHART_SUPPORT = ["Access Point", "Wild Cam"]
DATE_FORMAT = "%Y-%m-%d"
TIMEZONE = "Europe/Zurich"

SETTINGS_DRAWER_WIDTH = 320 
CHART_DRAWER_HEIGHT = 500
ALERT_DURATION = 4000

REFRESH_KEY_TIME_LEFT_S = 10 * 60

QUERY_PARAMS = {
        "start": None, 
        "end": None, 
        "timerange": None, 
        "lat": 47.5339807306196, 
        "lon": 7.6169566067567, 
        "zoom": 12, 
        "tags": None, 
        "devices": None, 
        "node_label": None, 
        "note_id": None, 
        "env_id": None
        }

PRIMARY_COLOR = "mitwelten_green"
SECONDARY_COLOR = [
                '#FCE4EC',
                '#F8BBD0',
                '#F48FB1',
                '#F06292',
                '#EC407A',
                '#E91E63',
                '#D81B60',
                '#C2185B',
                '#AD1457',
                '#880E4F',
            ],

BACKGROUND_COLOR = "#E8F7FC"

app_theme = {
    "colors": {
        PRIMARY_COLOR:
            [
                "#e7fafa",
                "#deeded",
                "#c1d7d7",
                "#a2c1c1",
                "#88aeae",
                "#76a3a3",
                "#6c9d9d",
                "#598888",
                "#4b7a7a",
                "#366a6a"
                ],
    },
    "primaryColor": PRIMARY_COLOR,
}


EXCLUDED_DEPLOYMENTS = ["Access Point", "Phaeno Cam"]

CONFIRM_UNSAVED_CHANGES_MESSAGE = "You have unsaved changes. Do you want to discard them?"
CONFIRM_DELETE_MESSAGE          = "Are you sure you want to permanently remove this item?"

supported_mime_types = dict(
        image = ["image/png", "image/jpg", "image/jpeg", "image/gif", "image/webp"],
        audio = ["audio/mpeg"],
        doc   = ["application/pdf", "text/plain"],
        )


thumbnail_size = (64, 64)


PAX_DESCRIPTION = "PAX counters are used to detect the presence of humans by anonymously capturing the signals generated by their smartphones. The diagram shows the number of detections per time unit. You can select a shorter time frame by holding down the mouse button and dragging over the measurement data in the diagram or by using the small menu at the top right."
AUDIO_DESCRIPTION = "Audio loggers are used to record bird calls. With the help of machine learning, thes are analysed and assigned to the different species. The diagram shows the bird species detected per day (colour-coded). You can select a shorter time frame by holding down the mouse button and dragging over the measurement data in the diagram or by using the small menu at the top right."
POLLINATOR_DESCRIPTION = "Cameras mounted above flower pots were used to record pollinating insects and 5 different morphospicies were counted using artificial intelligence. You can select a shorter time frame by holding down the mouse button and dragging over the measurement data in the diagram or by using the small menu at the top right."
ENVIRONMENT_SENSOR_DESCRIPTION = "Sensors were used to measure temperature, humidity and soil moisture. You can select a shorter time frame by holding down the mouse button and dragging over the measurement data in the diagram or by using the small menu at the top right."
HABITAT_DESCRIPTION = "The quality of the habitat type is determined on the basis of 10 criteria."
EXPERIMENT_AND_FINDING_DESCRIPTION = "Short documentations of the conducted experiments and summaries of the findings."
WILD_CAM_DESCRIPTION = "Wildlife cameras were used to record images of the animal world."
DISCOVER_DESCRIPTION = 'The research project uses the lens of co-worlding to develop environmental media approaches that aim to support and foster biodiversity in urban areas by extending design research to natural, cultural and media sciences. In the project’s three case studies, media infrastructures were installed in three sites of human-environment entanglements: in the Merian Gardens near Basel, in a former port area of the city of Basel, and in a nature reserve in Reinach (Basel agglomeration). "Discover" is a map-based publication of the research results prepared for the public.'

