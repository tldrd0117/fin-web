import os
from watchdog.observers import Observer
from pymitter import EventEmitter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.observer.CmdFileSystemEventHandler import CmdFileSystemEventHandler


class DownloadObserver(object):
    def startObserver(self, uuid: str, ee: EventEmitter) -> None:
        # curdir = os.path.dirname(__file__)
        relPath = os.path.relpath(f"../downloads/{uuid}", start=os.curdir)
        path = os.path.realpath(relPath)
        # path = "/Users/iseongjae/Downloads/"
        print(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.event_handler = CmdFileSystemEventHandler(ee)
        self.event_handler.setDownloadTask(self)
        # log_handler = LoggingEventHandler()
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=False)
        # observer.schedule(log_handler, path, recursive=False)
        self.observer.daemon = True
        self.observer.start()

    def stopObserver(self) -> None:
        self.observer.stop()
