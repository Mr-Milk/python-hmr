__all__ = ['Reloader']

from importlib.util import find_spec, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import List, Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from hmr.reload import ReloadModule, ReloadObject


class EventsHandler(FileSystemEventHandler):
    module = None
    object = None
    excluded = None

    def on_modified(self, event):
        # print(f"File modified, reloading {self.module}")
        ReloadModule(self.module, excluded=self.excluded).fire(self.module)
        if self.object is not None:
            self.object.fire()


class Reloader:
    module = None
    object = None
    object_type = None
    excluded = None
    observer = None
    watch = None

    def __init__(self, obj, excluded=None):
        if isinstance(obj, ModuleType):
            self.object_type = ModuleType
            self.module = obj
        elif isinstance(obj, Callable):
            self.object_type = Callable
            self.module = module_from_spec(find_spec(obj.__module__))
            self.object = ReloadObject(obj, self.module)
        else:
            raise TypeError("Hot Module Reload are supported for Module, Function and Class; "
                            "Can't reload a static variable since we can't resolve its source"
                            ", try access it from the reloaded module. eg. my_module.variable")

        if isinstance(excluded, List):
            self.excluded = excluded

        path = Path(self.module.__spec__.origin).parent
        # print(f"Monitor {path}")
        event_handler = EventsHandler()
        event_handler.module = self.module
        event_handler.excluded = self.excluded
        if self.object is not None:
            event_handler.object = self.object
        observer = Observer()
        self.observer = observer
        self.watch = observer.schedule(event_handler, path, recursive=True)
        observer.setDaemon(True)
        observer.start()

    def stop(self):
        self.observer.unschedule(self.watch)

    def __call__(self, *args, **kwargs):
        return self.object.__call__(*args, **kwargs)

    def __getattr__(self, name):
        if self.object_type is ModuleType:
            return getattr(self.module, name)
        else:
            return getattr(self.object, name)
