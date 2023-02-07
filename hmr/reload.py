import sys
import warnings
import weakref
from importlib import reload, invalidate_caches, import_module
from importlib.util import module_from_spec, find_spec
from pathlib import Path
from types import ModuleType, FunctionType


def _recursive_reload(module, excluded):
    reload(sys.modules.get(module.__name__))
    for attr in dir(module):
        attr = getattr(module, attr)
        if isinstance(attr, ModuleType):
            if attr.__name__.startswith(module.__name__):
                if attr.__name__ not in excluded:
                    _recursive_reload(attr, excluded)


def get_module_by_name(name):
    return module_from_spec(find_spec(name))


class ModuleReloader:

    def __init__(self, module, excluded=None):
        # If user import a submodule
        # we still need to monitor the whole module for rerun
        entry_module = get_module_by_name(module.__name__.split(".")[0])
        self.module = module
        self.entry_module = entry_module
        self.excluded = [] if excluded is None else excluded

    def __getattr__(self, name):
        return getattr(self.module, name)

    def fire(self):
        invalidate_caches()
        _recursive_reload(self.entry_module, self.excluded)
        self.module = import_module(self.module.__name__)
        self.entry_module = import_module(self.entry_module.__name__)

    def get_module_path(self):
        return Path(self.entry_module.__spec__.origin).parent


class ObjectReloader(ModuleReloader):

    def __init__(self, obj, excluded=None):

        self.object = obj
        self.is_func = isinstance(obj, FunctionType)
        self.object_name = obj.__name__

        self.object_module = get_module_by_name(obj.__module__)

        self.object_file = self.object_module.__spec__.origin
        self.original_object = obj
        self._instances = []  # Keep references to all instances
        super().__init__(self.object_module, excluded=excluded)

    def __call__(self, *args, **kwargs):
        instance = self.object.__call__(*args, **kwargs)
        if not self.is_func:
            # When the class initiate
            # Register a reference to the instance
            # So we can replace it later
            self._instances.append(weakref.ref(instance))
        return instance

    def __getattr__(self, name):
        return getattr(self.object, name)

    def fire(self) -> None:
        """Reload the object"""
        super().fire()
        with open(self.object_file, 'r') as f:
            source_code = f.read()
        locals_: dict = {}
        exec(source_code, self.module.__dict__, locals_)
        self.object = locals_.get(self.object_name, None)
        if self.object is None:
            self.object = self.original_object
            warnings.warn("Can't reload object. If it's a decorated function, "
                          "use functools.wraps to "
                          "preserve the function signature.", UserWarning)

        # Replace the old reference of all instances with the new one
        if not self.is_func:
            for ref in self._instances:
                instance = ref()  # We keep weak references to objects
                if instance:
                    instance.__class__ = self.object
