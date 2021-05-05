from pymitter import EventEmitter
from typing import Any
import logging
logger = logging.getLogger("eventemitter")


ee = EventEmitter()


@ee.on_any()
def allEvents(*args: Any, **kArgs: Any) -> None:
    val = []
    for key in kArgs:
        val.append(f"key:{key} value:{kArgs[key]}")
    for arg in args:
        val.append(str(arg))
    logger.debug(str(val)[0:1000])
