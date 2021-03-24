# sidenote:
#
# initially tried to use FastAPI, but since all of this is
# dynamic, it just feels like I'm fighting with its
# JSON encoder and its class-model based approach
#
# Custom Encoders through its json_enodable function
# run before any custom ones I define, so its not
# possible to serialize custom types
#
# at that point, I'm getting none of the benefits
# of the types that pydantic gives me, so its not
# particularly worth to use it

import os
from types import FunctionType
from typing import List, Dict, Any, Callable, Iterator, Tuple, Union, Optional
from functools import wraps

import more_itertools
from flask import Blueprint, request, Response
from my.core.serialize import dumps

from .common import FuncTuple

# generates a blueprint which
# represents the entire HPI interface
# module_name -> function information
# example item in the fdict:
#   'my.github.all': [('events', <function events ...>), (), ...]
def generate_blueprint(fdict: Dict[str, List[FuncTuple]]) -> Blueprint:
    blue: Blueprint = Blueprint("hpi_api", __name__)
    routes: List[str] = []
    for module_name, funcs in fdict.items():
        for (fname, libfunc) in funcs:
            rule: str = os.path.join("/", module_name.replace(".", "/"), fname)
            assert "." not in rule
            blue.add_url_rule(
                rule, rule, generate_route_handler(libfunc), methods=["GET"]
            )
            routes.append(rule)
    # add /route, to display all routes
    def all_routes() -> Any:
        return {"routes": sorted(routes)}

    blue.add_url_rule("/routes", "routes", all_routes, methods=["GET"])
    return blue


ResponseVal = Union[Response, Tuple[Any, int]]


# flask seems to handle serializing any vals I've tried so far
# routes that commonly fail:
#   /input functions (PosixPath is not JSON serializable)
#   any helper/util function which requires an argument
#
# dont have any items which return pandas.DataFrames, but
# that should be a simple check to convert it to an iterable-thing,
# if iter() doesnt already do it automatically
def jsonsafe(obj: Any) -> ResponseVal:
    """
    Catch the TypeError which results from encoding non-encodable types
    This uses the serialize function from my.core.serialize, which handles
    serializing most types in HPI
    """
    try:
        return Response(dumps(obj), status=200, headers={"Content-Type": "application/json"})
    except TypeError as encode_err:
        return {
            "error": "Could not encode response from HPI function as JSON",
            "exception": str(encode_err),
        }, 400


IntResult = Union[ResponseVal, int]

# helper to parse int GET params
def parse_int_or_error(get_param: Optional[str], default: int) -> IntResult:
    # if the request.args.get returned None, user didn't override default
    if get_param is None:
        return default
    try:
        return int(get_param)
    except ValueError as ve:
        # return error, structured as ResponseVal
        return {
            "error": f"Could not convert '{get_param}' to an integer",
            "exception": str(ve),
        }, 400


# TODO: let user pass basic kwargs as arguments? Can inspect type/signature.bind and coerce. could be dangerous...
def generate_route_handler(libfunc: FunctionType) -> Callable[[], ResponseVal]:
    """
    user can pass GET parameters:
    - limit: int (defaults to 50) - how many items to return per page
    - page: int (defaults to 1) - which page to return
    - sort: str "attribute_name" - some getattr/dictionary key on the object returned from the HPI function), e.g. "dt", or "date", to sort by date. If not provided, returns the same order as the underlying HPI function
    - order_by: one of [asc, desc] (default: asc) - to sort by ascending or descending order
    """

    @wraps(libfunc)
    def route() -> ResponseVal:
        # wrap TypeError, common for non-event-like functions to fail
        # when argument count doesnt match
        try:
            resp: Any = libfunc()
        except TypeError as e:
            return {
                "error": "TypeError calling HPI function, assuming not enough arguments passed",
                "exception": str(e),
            }, 400
        except Exception as e:
            return {"error": "Error calling HPI function", "exception": str(e)}, 400

        # if primitive, stats or dict, return directly
        if (
            any([isinstance(resp, _type) for _type in [int, float, str, bool]])
            or isinstance(resp, dict)
            or libfunc.__qualname__ == "stats"
        ):
            return jsonsafe({"value": resp})

        # else, assume this returns event/namedtuple/object-like
        riter: Iterator[Any] = iter(resp)

        # parse GET arguments

        # parse limit GET arg
        limit_res: IntResult = parse_int_or_error(request.args.get("limit"), 50)
        if not isinstance(limit_res, int):
            return limit_res
        limit: int = limit_res
        # TODO: modularize into parse_int_or_error?
        if limit < 1:
            return {"error": "limit must be greater than or equal to 1"}, 400

        # parse page GET arg
        page_res: IntResult = parse_int_or_error(request.args.get("page"), 1)
        if not isinstance(page_res, int):
            return page_res
        page: int = page_res
        if page < 1:
            return {"error": "page must be greater than or equal to 1"}, 400

        # parse sort GET arg
        if "sort" in request.args:
            # peek at first item, to determine how to iterate over this
            # if values are a dict, should index, else use getattr
            val: Any = more_itertools.peekable(riter).peek()
            key: str = request.args["sort"]
            if isinstance(val, dict):
                # make sure dictionary has key
                if key not in val.keys():
                    return {
                        "error": f"Value returned from iterator is a dictionary, but couldn't find key '{key}'"
                    }, 400
                riter = iter(sorted(riter, key=lambda v: v[key]))  # type: ignore[no-any-return]
            else:
                # if isn't a dict, assume namedtuple-like, or can use getattr on the object
                if not hasattr(val, key):
                    return {
                        "error": f"Value returned from iterator doesn't have attribute '{key}'"
                    }, 400
                riter = iter(sorted(riter, key=lambda v: getattr(v, key)))  # type: ignore[no-any-return]

        # parse order_by GET arg
        if "order_by" in request.args and request.args["order_by"] == "desc":
            riter = more_itertools.always_reversible(riter)

        # exhaust paginations for 'previous' pages
        for _ in range(page - 1):
            more_itertools.take(limit, riter)  # take into the void

        return jsonsafe(
            {"page": page, "limit": limit, "items": more_itertools.take(limit, riter)}
        )

    return route
