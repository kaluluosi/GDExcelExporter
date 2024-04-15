from . import logger  # noqa: F401
import importlib.metadata

__version__ = importlib.metadata.version(__package__)  # type: ignore
