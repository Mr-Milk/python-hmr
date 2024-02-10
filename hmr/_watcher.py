from __future__ import annotations

__all__ = ["Watchers"]

import atexit
import sys
import traceback
from datetime import datetime
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ._reload import BaseReloader

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch


class EventsHandler(FileSystemEventHandler):
    reload_list = []
    _last_error = None

    def on_any_event(self, event):
        # print(event.src_path, event.event_type, event.is_directory)
        # print("Reload list", self.reload_list)
        for reloader in self.reload_list:
            try:
                reloader.__reload__()
            except Exception:
                _current = datetime.now()
                error_stack = traceback.extract_stack()
                # only fire the same error once
                if self._last_error is None or self._last_error != error_stack:
                    self._last_error = error_stack
                    traceback.print_exc(file=sys.stderr)
        return


class WatcherStorage:
    def __init__(self):
        self._observer = None
        self.watchers: Dict[str, (ObservedWatch, EventsHandler)] = {}

        atexit.register(self.__del__)

    @property
    def observer(self) -> Observer:
        if self._observer is None:
            self._observer = Observer()
            self._observer.daemon = True
            self._observer.start()
        return self._observer

    def add_reload(self, reloader: BaseReloader):
        root_path = reloader.__proxy_module__.root_path
        watcher = self.watchers.get(root_path)
        if watcher is None:
            event_handler = EventsHandler()
            event_handler.reload_list.append(reloader)
            watch = self.observer.schedule(event_handler, root_path, recursive=True)
            self.watchers[root_path] = (watch, event_handler)
        else:
            watch, event_handler = watcher
            event_handler.reload_list.append(reloader)

    def delete_reload(self, reloader: BaseReloader):
        root_path = reloader.__proxy_module__.root_path
        watcher = self.watchers.get(root_path)
        if watcher is not None:
            watch, event_handler = watcher
            # This may be emitted multiple times
            # Must wrap in a try-except block
            try:
                event_handler.reload_list.remove(reloader)
                if not event_handler.reload_list:
                    self.observer.unschedule(watch)
                    del self.watchers[root_path]
            except (ValueError, KeyError):
                pass

    def __del__(self):
        if self._observer is not None:
            self._observer.unschedule_all()
            self._observer.stop()
            self._observer.join()


Watchers = WatcherStorage()


# def get_watchers():
#     return Watchers
