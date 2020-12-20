from typing import List, Dict

from flask import Flask

from .common import FuncTuple
from .discovery import iter_modules, iter_functions
from .routes import generate_blueprint


def generate_server(app_name: str = "hpi_api") -> Flask:
    app: Flask = Flask(app_name)
    fdict: Dict[str, List[FuncTuple]] = {}
    for mod in iter_modules():
        fdict[mod.name] = list(iter_functions(mod))
    app.register_blueprint(generate_blueprint(fdict))
    return app
