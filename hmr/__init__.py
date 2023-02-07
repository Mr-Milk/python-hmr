"""Hot module reload for python"""

__all__ = ["reload", "Reloader"]
__version__ = "0.2.0"

from .api import Reloader
reload = Reloader
