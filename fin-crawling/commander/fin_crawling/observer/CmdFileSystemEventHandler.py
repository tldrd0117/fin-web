
from watchdog.events import FileSystemEventHandler

class CmdFileSystemEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        """Catch-all event handler.
        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """

    def on_moved(self, event):
        """Called when a file or a directory is moved or renamed.
        :param event:
            Event representing file/directory movement.
        :type event:
            :class:`DirMovedEvent` or :class:`FileMovedEvent`
        """

    def on_created(self, event):
        """Called when a file or directory is created.
        :param event:
            Event representing file/directory creation.
        :type event:
            :class:`DirCreatedEvent` or :class:`FileCreatedEvent`
        """
        print("created")
        print(event)

    def on_deleted(self, event):
        """Called when a file or directory is deleted.
        :param event:
            Event representing file/directory deletion.
        :type event:
            :class:`DirDeletedEvent` or :class:`FileDeletedEvent`
        """

    def on_modified(self, event):
        """Called when a file or directory is modified.
        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """

    def on_closed(self, event):
        """Called when a file opened for writing is closed.
        :param event:
            Event representing file closing.
        :type event:
            :class:`FileClosedEvent`
        """