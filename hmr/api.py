__all__ = ['Reloader']

from importlib import invalidate_caches
from importlib.util import find_spec, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import List, Callable, Optional, Union, Any

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from hmr.reload import ModuleReloader, ObjectReloader


class EventsHandler(FileSystemEventHandler):
    reloader = None

    def on_any_event(self, event):
        self.reloader.fire()


class Reloader:
    """The reloader to proxy reloaded object

    Args:
        obj: The object to be monitored and
            reloaded when file changes on the disk
        excluded: Excluded the module that you don't want to be reloaded


    """

    def __init__(self,
                 obj: Any,
                 excluded=None
                 ):

        if isinstance(obj, ModuleType):
            self.reloader = ModuleReloader(obj, excluded)
        elif isinstance(obj, Callable):
            self.reloader = ObjectReloader(obj, excluded)
        else:
            msg = "Hot Module Reload supports Module, Function and Class; " \
                  "Do not pass initialize class or function, " \
                  "use `func` not `func()`. " \
                  "For static variable " \
                  "access it from the module like `module.var`"
            raise TypeError(msg)

        path = self.reloader.get_module_path()
        event_handler = EventsHandler()
        event_handler.reloader = self.reloader
        observer = Observer()
        self.observer = observer
        self.watch = observer.schedule(event_handler, path, recursive=True)
        observer.setDaemon(True)
        observer.start()

    def __stop__(self):
        """Shutdown the monitor"""
        self.observer.unschedule_all()
        self.observer.stop()

    def __del__(self):
        return self.__stop__()

    def __getattr__(self, name):
        return self.reloader.__getattr__(name)

    def __call__(self, *args, **kwargs):
        return self.reloader.__call__(*args, **kwargs)
