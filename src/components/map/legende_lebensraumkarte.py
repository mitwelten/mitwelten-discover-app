import dash_mantine_components as dmc
from src.config.id_config import *

legende_lebensraumkarte = dmc.Affix(
                id=ID_AFFIX_LEBENSRAUM_LEGENDE,
                display="none",
                h=100,
                bottom=67,
                right=45,
                bg="#ffffff80",
                children=[
                    dmc.ScrollArea(
                        h=100,
                        children=[
                            dmc.Image(src="assets/lebensraumkarte_legende.png")
                            ]
                        ),
                    ], 
                )
