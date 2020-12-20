"""
Handles discovering the HPIModule objects from my.core.util
"""

import importlib
import inspect
from types import FunctionType
from typing import Any, Iterator, Tuple, Optional

from my.core.util import modules
from my.core.core_config import config as coreconf

from .log import logger
from .common import HPIModule, FuncTuple

# initially was a copy of my.core._modules
#
# this doesnt check skip_reason like that does
# because 'all' modules (e.g. github.all) often don't
# have stats, but you'd definitely want to use
# them as modules (since it has the top level merged events func)
#
# however, we still need to check if a module is disabled in user config (disabled_modules)
def iter_modules() -> Iterator[HPIModule]:
    for mod in modules():
        active: Optional[bool] = coreconf._is_module_active(mod.name)
        if active is False:
            continue
        yield mod


# this takes some liberties with what should be
# an entrypoint to the module
# it assumes:
#   - the function was defined as a top-level function in the module (its not a [relative] import)
#   - the function doesnt start with an underscore (those are typically helper/internal functions)
def iter_functions(mod: HPIModule) -> Iterator[FuncTuple]:
    try:
        modval = importlib.import_module(mod.name)
        for (fname, func) in inspect.getmembers(modval, inspect.isfunction):
            # make sure function was defined in module
            if func.__module__ == mod.name:
                # assume its not a helper function
                if not fname.startswith("_"):
                    yield (fname, func)
    except Exception as e:
        logger.error("Error listing functions, " + str(e))
        logger.warning(
            "If you wish to silence this error, add the name of this module to the list of disabled_modules in my.config.core in your HPI configuration"
        )


# -- dont use out of the box; dangerous to just call every function in a module

# returns True if a function from a HPI module
# returns a stream of (at least 1) event(s)
#
# this isn't perfect as it does find
# false-positives, but it should
# filter out some functions
def is_event_like(func: FunctionType, args: Optional[Tuple[Any, ...]] = None) -> bool:
    rargs: Tuple[Any, ...] = () if args is None else args
    try:
        resp_iter: Any = iter(func(*rargs))
        next(resp_iter)
        # didnt error, continue
        return True
    except Exception as e:
        logger.debug(f"Could not apply {func} with {args}: " + str(e))
    return False
