DEFAULT_LAT = 47.53522891224535
DEFAULT_LON = 7.606299048260731
DEFAULT_ZOOM = 11.5
DEFAULT_MAX_ZOOM = 20.9
DEFAULT_MAP_INDEX = 1
DEFAULT_MARKER_COLORS = [
    "#FF5733",  # (Pastell Orange)
    "#9B59B6",  # (Lavendelviolett)
    "#F1C40F",  # (Sonnenblumengelb)
    "#3498DB",  # (Hellblau)
    "#E67E22",  # (Terra Cotta)
    "#2ECC71",  # (Smaragdgrün)
    "#E74C3C",  # (Tomatenrot)
    "#1ABC9C",  # (Türkis)
    "#F39C12",  # (Goldgelb)
    "#FF00FF",  # (Magenta)
]


class MapConfiguration:

    def __init__(
            self,
            title,
            image,
            index,
            source,
            source_attribution,
    ):
        self.title = title
        self.image = image
        self.index = index
        self.source = source
        self.source_attribution = source_attribution


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
