from __future__ import annotations

__all__ = ["reload"]

from types import ModuleType
from typing import List, Callable, Sequence, Union

from hmr._reload import ModuleReloader, ObjectReloader

Reloadable = Union[ModuleType, Callable]
Reloader = Union[ModuleReloader, ObjectReloader]


def reload(
    *obj: Reloadable | Sequence[Reloadable], exclude: Sequence[str] = None
) -> Reloader | List[Reloader]:
    """The reloader to proxy reloaded object

    Parameters
    ----------
    obj : The object(s) to be monitored and
        reloaded when file changes on the disk
    exclude : Exclude the module that you don't want to be reloaded

    """
    reloaders = []

    if len(obj) == 1:
        if isinstance(obj[0], (list, tuple)):
            obj_list = obj[0]
        else:
            obj_list = obj
    else:
        obj_list = obj

    for obj in obj_list:
        if isinstance(obj, ModuleType):
            reloader = ModuleReloader(obj, exclude)
        elif isinstance(obj, Callable):
            reloader = ObjectReloader(obj, exclude)
        else:
            msg = (
                f"Operation failed: {obj} is either a constant value or "
                f"an already initialized object and cannot be reloaded. "
                "To resolve this issue: "
                "1. If you're attempting to pass a function or class, "
                "use its name without parentheses (e.g., `func` instead of `func()`). "
                "2. To access a constant, refer to it directly from its module "
                "using dot notation (e.g., `module.var`)."
            )

            raise TypeError(msg)
        reloaders.append(reloader)
    if len(reloaders) == 1:
        return reloaders[0]
    return reloaders
