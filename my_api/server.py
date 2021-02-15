from typing import List, Dict

from flask import Flask, Response

from .common import FuncTuple
from .discovery import iter_modules, iter_functions
from .routes import generate_blueprint


def generate_server(app_name: str = "hpi_api", cors: bool = True) -> Flask:
    app: Flask = Flask(app_name)
    fdict: Dict[str, List[FuncTuple]] = {}
    for mod in iter_modules():
        fdict[mod.name] = list(iter_functions(mod))
    app.register_blueprint(generate_blueprint(fdict))

    if cors:

        @app.after_request
        def after_request(response: Response) -> Response:
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

    return app
