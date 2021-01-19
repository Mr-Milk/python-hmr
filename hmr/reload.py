import sys
import weakref
from importlib import reload
from types import ModuleType, FunctionType
from typing import List

from redbaron import RedBaron


class ReloadModule:
    module = None
    excluded = []

    def __init__(self, module, excluded=None):
        if isinstance(module, ModuleType):
            self.module = module
        else:
            raise TypeError("Must be a ModuleType")

        if isinstance(excluded, List):
            self.excluded = excluded

    def fire(self, module):
        reload(sys.modules.get(module.__name__))
        for attr in dir(module):
            attr = getattr(module, attr)
            if isinstance(attr, ModuleType):
                if attr.__name__.startswith(module.__name__):
                    if attr.__name__ not in self.excluded:
                        self.fire(attr)


class ReloadObject:

    def __init__(self, obj, module):
        self.object = obj
        self.is_func = isinstance(obj, FunctionType)
        self.object_name = obj.__name__
        self.object_module = module
        self.object_file = module.__spec__.origin
        self.original_object = obj
        self._instances = []  # Keep references to all instances

    def __call__(self, *args, **kwargs):
        instance = self.object.__call__(*args, **kwargs)
        if not self.is_func:
            # Register a reference to the instance
            self._instances.append(weakref.ref(instance))
        return instance

    def __getattr__(self, name):
        return self.object.__getattr__(name)

    def fire(self) -> None:
        try:
            with open(self.object_file, 'r') as f:
                source_code = f.read()
            ast = RedBaron(source_code)
            query_literal = 'def' if self.is_func else 'class'
            source = ast.find_all(query_literal, name=self.object_name)[0].dumps()
            locals_: dict = {}
            exec(source, self.object_module.__dict__, locals_)
            self.object = locals_[self.object_name]
            # Replace the old reference of all instances with the new one
            if not self.is_func:
                for ref in self._instances:
                    instance = ref()  # We keep weak references to objects
                    if instance:
                        instance.__class__ = self.object
        except SyntaxError as error:
            print('SyntaxError', error)
