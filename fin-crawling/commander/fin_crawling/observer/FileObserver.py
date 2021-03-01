import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from .CmdFileSystemEventHandler import CmdFileSystemEventHandler

def observe():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    curdir = os.path.dirname(__file__)
    relPath = os.path.relpath("../downloads",start=os.curdir)
    path = os.path.realpath(relPath)
    print(path)
    event_handler = CmdFileSystemEventHandler()
    log_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.schedule(log_handler, path, recursive=False)
    observer.daemon = True
    observer.start()
    return observer
    # try:
    #     while True:
    #         time.sleep(1)
    #         print("observerRunning")
    # finally:
    #     observer.stop()
    #     observer.join()


