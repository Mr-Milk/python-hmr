from __future__ import annotations

__all__ = ["ModuleReloader", "ObjectReloader", "BaseReloader"]

import sys
import warnings
import weakref
from dataclasses import dataclass
from importlib import reload, invalidate_caches, import_module
from importlib.util import module_from_spec, find_spec
from pathlib import Path
from types import ModuleType, FunctionType
from typing import Set

from ._watcher import Watchers


def _recursive_reload(module, exclude):
    reload(sys.modules.get(module.__name__))
    for attr in dir(module):
        attr = getattr(module, attr)
        if isinstance(attr, ModuleType):
            if attr.__name__.startswith(module.__name__):
                if attr.__name__ not in exclude:
                    _recursive_reload(attr, exclude)


def get_module_by_name(name):
    return module_from_spec(find_spec(name))


@dataclass
class ProxyModule:
    name: str
    file: str
    root_name: str
    root_path: str
    object: object | ModuleType | FunctionType
    root_object: ModuleType
    exclude: Set[str] = None

    def is_func(self):
        return isinstance(self.object, FunctionType)

    def reload(self):
        _recursive_reload(self.root_object, self.exclude)
        self.root_object = import_module(self.root_name)


class BaseReloader(ModuleType):
    __proxy_module__: ProxyModule

    def __init__(self, proxy_obj):
        obj = proxy_obj.object
        super().__init__(obj.__name__, obj.__doc__)
        self.__proxy_module__ = proxy_obj
        Watchers.add_reload(self)
        # Try to reload the module when the object is created
        self.__reload__()

    def __repr__(self):
        return f"<HMR for {self.__proxy_module__.object}>"

    def __getattr__(self, name):
        return getattr(self.__proxy_module__.object, name)

    def __del__(self):
        Watchers.delete_reload(self)

    # For IDE auto-completion
    @property
    def __all__(self) -> list:
        if hasattr(self.__proxy_module__.object, "__all__"):
            return self.__proxy_module__.object.__all__
        return []

    # For IDE auto-completion
    def __dir__(self):
        return self.__proxy_module__.object.__dir__()

    def __reload__(self) -> None:
        raise NotImplementedError


class ModuleReloader(BaseReloader):
    def __init__(self, module, exclude=None):
        # If user import a submodule
        # we still need to monitor the whole module to reload
        if exclude is None:
            exclude = set()
        else:
            exclude = set(exclude)

        root_module = get_module_by_name(module.__name__.split(".")[0])
        root_path = Path(root_module.__spec__.origin).parent
        proxy = ProxyModule(
            name=module.__name__,
            file=module.__spec__.origin,
            root_name=root_module.__name__,
            root_path=str(root_path),
            object=module,
            root_object=root_module,
            exclude=exclude,
        )

        super().__init__(proxy)

    def __reload__(self):
        invalidate_caches()
        self.__proxy_module__.reload()


class ObjectReloader(BaseReloader):
    def __init__(self, obj, exclude=None):
        root_module = get_module_by_name(obj.__module__)
        root_path = Path(root_module.__spec__.origin).parent

        if exclude is None:
            exclude = set()
        else:
            exclude = set(exclude)

        proxy = ProxyModule(
            name=obj.__name__,
            file=root_module.__spec__.origin,
            root_name=root_module.__name__,
            root_path=str(root_path),
            object=obj,
            root_object=get_module_by_name(obj.__module__),
            exclude=exclude,
        )

        self.__ref_instances = []  # Keep references to all instances
        super().__init__(proxy)

    def __call__(self, *args, **kwargs):
        # When user override the __call__ method in class
        try:
            instance = self.__proxy_module__.object.__call__(*args, **kwargs)
        except TypeError:
            instance = self.__proxy_module__.object(*args, **kwargs)
        if not self.__proxy_module__.is_func():
            # When the class initiate
            # Register a reference to the instance
            # So we can replace it later
            self.__ref_instances.append(weakref.ref(instance))
        return instance

    def __reload__(self) -> None:
        """Reload the object"""
        invalidate_caches()
        self.__proxy_module__.reload()
        with open(self.__proxy_module__.file, "r") as f:
            source_code = f.read()
        locals_: dict = {}
        exec(source_code, self.__proxy_module__.root_object.__dict__, locals_)
        updated_object = locals_.get(self.__proxy_module__.name, None)
        if updated_object is None:
            warnings.warn(
                "Can't reload object. If it's a decorated function, "
                "use functools.wraps to "
                "preserve the function signature.",
                UserWarning,
            )
        else:
            self.__proxy_module__.object = updated_object

            # Replace the old reference of all instances with the new one
            if not self.__proxy_module__.is_func():
                for ref in self.__ref_instances:
                    instance = ref()  # We keep weak references to objects
                    if instance:
                        instance.__class__ = updated_object
