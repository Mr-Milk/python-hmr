__all__ = ['Reloader']

import atexit
from importlib.util import find_spec, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import List, Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from hmr.reload import ReloadModule, ReloadObject

observer = Observer()


def quit_watchdog():
    try:
        observer.stop()
        observer.join()
    except Exception:
        pass


atexit.register(quit_watchdog)


class EventsHandler(FileSystemEventHandler):
    module = None
    object = None

    def on_modified(self, event):
        # print(f"File modified, reloading {self.module}")
        ReloadModule(self.module).fire(self.module)
        if self.object is not None:
            self.object.fire()


class Reloader:
    module = None
    object = None
    object_type = None

    def __init__(self, obj, excluded=None):
        if isinstance(obj, ModuleType):
            self.object_type = ModuleType
            self.module = obj
        elif isinstance(obj, Callable):
            self.object_type = Callable
            self.module = module_from_spec(find_spec(obj.__module__.split(".")[0]))
            self.object = obj
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
        if self.object is not None:
            self.object = ReloadObject(self.object, self.module)
            event_handler.object = self.object
        observer.schedule(event_handler, path, recursive=True)
        try:
            observer.setDaemon(True)
            observer.start()
        except Exception:
            pass

    def __call__(self, *args, **kwargs):
        return self.object.__call__(*args, **kwargs)

    def __getattr__(self, name):
        if self.object_type is ModuleType:
            return getattr(self.module, name)
        else:
            return self.object.__getattr__(name)
