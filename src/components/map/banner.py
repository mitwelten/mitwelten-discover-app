from dash import html
from src.config.id_config import ID_LOGO_CONTAINER

mitwelten_bannner = html.Div( 
                             children=html.A(
                                 "MITWELTEN",
                                 title="mitwelten.org",
                                 href="https://mitwelten.org",
                                 target="_blank",
                                 className="mitwelten-logo",
                                 ),
                             id=ID_LOGO_CONTAINER,
                             )
