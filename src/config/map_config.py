from src.model.map_configuration import MapConfiguration

DEFAULT_LAT = 47.53522891224535
DEFAULT_LON = 7.606299048260731
DEFAULT_ZOOM = 11.5
DEFAULT_MAX_ZOOM = 19
DEFAULT_MAP_INDEX = 1

MAP_TYPES = ["base", "overlay"]

SOURCE_PROPS = {
#    "Access Point":  dict(color="#FF5733", marker="location-0.svg", type="physical"),
    "Audio Logger":   dict(name="Audio Logger",           color="#99FFFF", marker="assets/markers/audioLogger.svg",   type="physical"),
    "Env Sensor":     dict(name="Environmental Sensor",   color="#9999FF", marker="assets/markers/environSensor.svg", type="physical"),
    "Pax Counter":    dict(name="Pax Counter",            color="#FF9999", marker="assets/markers/paxCounter.svg",    type="physical"),
    "Pollinator Cam": dict(name="Pollinator Camera",      color="#FFCCFF", marker="assets/markers/polliCam.svg",      type="physical"),
    "Wild Cam":       dict(name="Wild Camera",            color="#FFCC99", marker="assets/markers/wildCam.svg",       type="physical"),
    "Environment":    dict(name="Habitat Type",           color="#CCFF99", marker="assets/markers/habitat.svg",       type="virtual"),
    "Note":           dict(name="Experiments & Findings", color="#FFFF99", marker="assets/markers/docu.svg",          type="virtual"),
}


def get_source_props(source):
    return SOURCE_PROPS.get(source, {})


MAPS = [
    MapConfiguration(
        title="Open Street Map",
        image="./assets/minimap/open-street.png",
        index=0,
        source="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        source_attribution='© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    ),
    MapConfiguration(
        title="Swiss Topo Picture",
        image="./assets/minimap/swiss-topo-picture.png",
        index=1,
        source="https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg",
        source_attribution='<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    ),
    MapConfiguration(
        title="Swiss Topo Grey",
        image="./assets/minimap/swiss-topo-grey.png",
        index=2,
        source="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg",
        source_attribution='<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    ),
    MapConfiguration(
        title="Swiss Topo Color",
        image="./assets/minimap/swiss-topo-color.png",
        index=3,
        source="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg",
        source_attribution='<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    ),

]

OVERLAYS = [
    MapConfiguration(
        title="No Overlay",
        image="./assets/minimap/no-map.png",
        index=0,
        source="",
        source_attribution="",
    ),
    MapConfiguration(
        title="Lebensraum",
        image="./assets/minimap/lebensraum.png",
        index=1,
        source="https://wmts9.geo.admin.ch/1.0.0/ch.bafu.lebensraumkarte-schweiz/default/current/3857/{z}/{x}/{y}.png",
        source_attribution="<a href='https://www.bafu.admin.ch/bafu/de/home.html' target='_blank'>BAFU</a>",
    ),
    MapConfiguration(
        # title="Vegetationshöhen Modell LFI",
        title="Vegetation",
        image="./assets/minimap/vegetation.png",
        index=2,
        source="https://wmts9.geo.admin.ch/1.0.0/ch.bafu.landesforstinventar-vegetationshoehenmodell/default/current/3857/{z}/{x}/{y}.png",
        source_attribution="<a href='https://www.bafu.admin.ch/bafu/de/home.html' target='_blank'>BAFU</a>",
    ),
    MapConfiguration(
        title="Oberfläche",
        # title="Oberfläche",
        image="./assets/minimap/oberflaechenmodell.png",
        index=3,
        source="https://wmts9.geo.admin.ch/1.0.0/ch.bafu.landesforstinventar-vegetationshoehenmodell_relief/default/current/3857/{z}/{x}/{y}.png",
        source_attribution="<a href='https://www.bafu.admin.ch/bafu/de/home.html' target='_blank'>BAFU</a>",
    )
]
