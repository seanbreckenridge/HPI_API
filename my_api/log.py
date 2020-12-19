from os import environ
import logging
from logzero import setup_logger  # type: ignore[import]

# https://docs.python.org/3/library/logging.html#logging-levels
loglevel: int = logging.WARNING  # (30)
if "HPI_API_LOGS" in environ:
    loglevel = int(environ["HPI_API_LOGS"])

# logzero handles this fine,
# can be imported/configured multiple times
logger = setup_logger(name="my_api", level=loglevel)
