import os
from pathlib import Path
from watchdog.observers import Observer
from pymitter import EventEmitter
from app.observer.CmdFileSystemEventHandler import CmdFileSystemEventHandler
import asyncio


class DownloadObserver(object):

    async def makePath(self, uuid: str) -> str:
        relPath = os.path.relpath(f"../downloads/{uuid}", start=os.curdir)
        path = os.path.realpath(relPath)
        # path = "/Users/iseongjae/Downloads/"
        print(f"makePath: {path}")
        try:
            if not os.path.exists(path):
                proc = await asyncio.create_subprocess_exec("mkdir", "-m", "777", path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await proc.communicate()
                print(stdout.decode())
                print(stderr.decode())
        except Exception as e:
            print(f"makePath error: {e}")
        
        return path

    def startObserver(self, path: str, ee: EventEmitter) -> None:
        # curdir = os.path.dirname(__file__)
        
        self.event_handler = CmdFileSystemEventHandler(ee)
        # self.event_handler.setDownloadTask(downloadTask)
        # log_handler = LoggingEventHandler()
        print(f"observePath:{path}")
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=True)
        # observer.schedule(log_handler, path, recursive=False)
        self.observer.daemon = False
        self.observer.start()

    def stopObserver(self) -> None:
        print("stopObserver")
        self.observer.stop()
        self.observer.join()
        self.observer = None
