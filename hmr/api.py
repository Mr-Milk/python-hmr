__all__ = ['Reloader']

import sys
from importlib.util import find_spec, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import List, Callable, Optional, Union, Any

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from hmr.reload import ReloadModule, ReloadObject


class EventsHandler(FileSystemEventHandler):
    reloader = None
    _last_error = None

    def on_any_event(self, event):
        try:
            self.reloader.reload()
        except Exception as e:
            # only fire the same error once
            if self._last_error != str(e):
                self._last_error = str(e)
                print(e, file=sys.stderr)


class Reloader:
    """The reloader to proxy reloaded object

    Args:
        obj: The object to be monitored and reloaded when file changes on the disk
        excluded: Excluded the module that you don't want to be reloaded, only works when obj is `ModuleType`

    Methods:
        reload: Reload the object
        stop: Stop the monitor process

    If you object happens to have the same attribute name as `reload` and `stop`, directly call obj.__getattr__(attr)
    to access your original attribute instead of the reloader's methods.

    """
    _module: Optional[ModuleType] = None
    _object: Union[Callable, ReloadObject, None] = None
    _object_type: Union[ModuleType, Callable, None] = None
    _excluded: List = None
    _last_error: str = None
    _observer: Optional[Observer] = None
    _watch: Optional[ObservedWatch] = None

    def __init__(self,
                 obj: Any,
                 excluded: Optional[List[str]] = None
                 ):
        if isinstance(obj, ModuleType):
            self._object_type = ModuleType
            self._module = obj
        elif isinstance(obj, Callable):
            self._object_type = Callable
            self._module = module_from_spec(find_spec(obj.__module__))
            self._object = ReloadObject(obj, self._module)
        else:
            raise TypeError("Hot Module Reload are supported for Module, Function and Class; Do not pass"
                            "initialized class or function, use `func` not `func()`. "
                            "If it's a static variable since we can't resolve its source"
                            ", try access it from the reloaded module. eg. my_module.variable")

        if isinstance(excluded, List):
            self._excluded = excluded

        path = Path(self._module.__spec__.origin).parent
        event_handler = EventsHandler()
        event_handler.reloader = self
        observer = Observer()
        self._observer = observer
        self._watch = observer.schedule(event_handler, str(path), recursive=True)
        observer.setDaemon(True)
        observer.start()

    def reload(self):
        """Reload the object"""
        ReloadModule(self._module, excluded=self._excluded).fire(self._module)
        if self._object is not None:
            self._object.fire()

    def stop(self):
        """Stop the monitor and reload"""
        self._observer.unschedule(self._watch)

    def __call__(self, *args, **kwargs):
        return self._object.__call__(*args, **kwargs)

    def __getattr__(self, name):
        if self._object_type is ModuleType:
            return getattr(self._module, name)
        else:
            return getattr(self._object, name)
