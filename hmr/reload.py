import sys
import warnings
import weakref
from importlib import reload, invalidate_caches
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


class ModuleReloader:

    def __init__(self, module, excluded=None):
        self.module = module
        self.module_name = self.module.__name__
        self.excluded = [] if excluded is None else excluded

    def __getattr__(self, name):
        return getattr(self.module, name)

    def fire(self):
        invalidate_caches()
        _recursive_reload(self.module, self.excluded)

    def get_module_path(self):
        return Path(self.module.__spec__.origin).parent


class ObjectReloader(ModuleReloader):

    def __init__(self, obj, excluded=None):

        self.object = obj
        self.is_func = isinstance(obj, FunctionType)
        self.object_name = obj.__name__

        object_module = module_from_spec(find_spec(obj.__module__))
        self.object_module = object_module
        self.object_file = object_module.__spec__.origin
        self.original_object = obj
        self._instances = None  # Keep references to all instances
        super().__init__(object_module, excluded=excluded)

    def __call__(self, *args, **kwargs):
        instance = self.object.__call__(*args, **kwargs)
        if not self.is_func:
            # Register a reference to the instance
            self._instances = weakref.ref(instance)
        return instance

    def __getattr__(self, name):
        return getattr(self.object, name)

    def fire(self) -> None:
        """Reload the object"""
        super().fire()
        with open(self.object_file, 'r') as f:
            source_code = f.read()
        locals_: dict = {}
        exec(source_code, self.object_module.__dict__, locals_)
        self.object = locals_.get(self.object_name, None)
        if self.object is None:
            self.object = self.original_object
            warnings.warn("Can't reload object. If it's a decorated function, "
                          "use functools.wraps to "
                          "preserve the function signature.", UserWarning)

        # Replace the old reference of all instances with the new one
        if not self.is_func:
            print(self._instances)
            instance = self._instances()  # We keep weak references to objects
            if instance:
                instance.__class__ = self.object
