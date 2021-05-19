
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileMovedEvent, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent
from app.model.dto import StockCrawlingDownloadTaskDTO
from pymitter import EventEmitter
from typing import Callable, Final

FILE_SYSTEM_HANDLER: Final[Callable] = lambda uuid: f"{uuid}/downloadComplete"


class CmdFileSystemEventHandler(FileSystemEventHandler):

    def __init__(self, ee: EventEmitter) -> None:
        self.ee = ee
    
    def setDownloadTask(self, downloadTask: StockCrawlingDownloadTaskDTO) -> None:
        self.downloadTask = downloadTask

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Catch-all event handler.
        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """

    def on_moved(self, event: FileMovedEvent) -> None:
        """Called when a file or a directory is moved or renamed.
        :param event:
            Event representing file/directory movement.
        :type event:
            :class:`DirMovedEvent` or :class:`FileMovedEvent`
        """

    def on_created(self, event: FileCreatedEvent) -> None:
        """Called when a file or directory is created.
        :param event:
            Event representing file/directory creation.
        :type event:
            :class:`DirCreatedEvent` or :class:`FileCreatedEvent`
        """
        # if self.queue.empty():
        #     print("####empty")
        #     return
        if not event.src_path.endswith(".csv"):
            print("####not exist")
            return
        self.ee.emit(FILE_SYSTEM_HANDLER(self.downloadTask.uuid), event, self.downloadTask)

    def on_deleted(self, event: FileDeletedEvent) -> None:
        """Called when a file or directory is deleted.
        :param event:
            Event representing file/directory deletion.
        :type event:
            :class:`DirDeletedEvent` or :class:`FileDeletedEvent`
        """

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Called when a file or directory is modified.
        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """
        # print("modified")
