__all__ = ['Reloader']

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

    def on_any_event(self, event):
        self.reloader.reload()


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
    module: Optional[ModuleType] = None
    object: Optional[Callable] = None
    object_type: Union[ModuleType, Callable, None] = None
    excluded: List = None
    observer: Optional[Observer] = None
    watch: Optional[ObservedWatch] = None

    def __init__(self,
                 obj: Any,
                 excluded: Optional[List[str]] = None
                 ):
        if isinstance(obj, ModuleType):
            self.object_type = ModuleType
            self.module = obj
        elif isinstance(obj, Callable):
            self.object_type = Callable
            self.module = module_from_spec(find_spec(obj.__module__))
            self.object = ReloadObject(obj, self.module)
        else:
            raise TypeError("Hot Module Reload are supported for Module, Function and Class; Do not pass"
                            "initialize class or function, use `func` not `func()`. "
                            "If it's a static variable since we can't resolve its source"
                            ", try access it from the reloaded module. eg. my_module.variable")

        if isinstance(excluded, List):
            self.excluded = excluded

        path = Path(self.module.__spec__.origin).parent
        event_handler = EventsHandler()
        event_handler.reloader = self
        observer = Observer()
        self.observer = observer
        self.watch = observer.schedule(event_handler, path, recursive=True)
        observer.setDaemon(True)
        observer.start()

    def reload(self):
        """Reload the object"""
        ReloadModule(self.module, excluded=self.excluded).fire(self.module)
        if self.object is not None:
            self.object.fire()
        # print(f"Reload success for {self.module.__spec__.name}")

    def stop(self):
        """Stop the monitor and reload"""
        self.observer.unschedule(self.watch)

    def __call__(self, *args, **kwargs):
        return self.object.__call__(*args, **kwargs)

    def __getattr__(self, name):
        if self.object_type is ModuleType:
            return getattr(self.module, name)
        else:
            return getattr(self.object, name)
