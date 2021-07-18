from __future__ import annotations
# from abc import ABC, abstractmethod
from typing import Any
import threading


class Crawler(object):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args: tuple, **kwargs: dict[str, Any]) -> Crawler:
        if not cls._instance:
            with cls._lock:
                # another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super(Crawler, cls).__new__(cls)
        return cls._instance
