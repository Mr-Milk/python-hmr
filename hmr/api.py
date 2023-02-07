__all__ = ['Reloader']

import sys

from datetime import datetime
from types import ModuleType
from typing import Callable, Any

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from hmr.reload import ModuleReloader, ObjectReloader


class EventsHandler(FileSystemEventHandler):
    reloader = None
    _last_error = None
    _updated = None

    def on_any_event(self, event):
        try:
            self.reloader.fire()
        except Exception as e:
            _current = datetime.now()
            # only fire the same error once
            if self._last_error != str(e):
                self._last_error = str(e)
                print(e, file=sys.stderr)
                return

            if (_current - self._updated).total_seconds() > 1:
                print(e, file=sys.stderr)
                return


class Reloader:
    """The reloader to proxy reloaded object

    Args:
        obj: The object to be monitored and
            reloaded when file changes on the disk
        excluded: Excluded the module that you don't want to be reloaded


    """
    _observer = None

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
        event_handler._updated = datetime.now()

        observer = Observer()
        self._observer = observer
        observer.schedule(event_handler, str(path),
                          recursive=True)
        observer.setDaemon(True)
        observer.start()

    def __stop__(self):
        """Shutdown the monitor"""
        if self._observer is not None:
            self._observer.unschedule_all()
            self._observer.stop()

    def __del__(self):
        return self.__stop__()

    def __getattr__(self, name):
        return getattr(self.reloader, name)

    def __call__(self, *args, **kwargs):
        return self.reloader.__call__(*args, **kwargs)
