from __future__ import annotations
from typing import Any, Callable, Dict, Tuple, Type, TypeVar
from pymitter import EventEmitter

T = TypeVar('T')


# class EventSubscriber(object):


class EventWrapper(object):
    instance: Any = None
    ee: EventEmitter = None
    onTarget: Dict = {}

    def __init__(self) -> None:
        super().__init__()

    def lazy_event_on(self1, cls: Type[T]) -> Any:
        class LazyEventClass(cls):
            def __init__(self, *args: Tuple, **kwargs: Dict) -> None:
                super().__init__(*args, **kwargs)
            
            def on_event(self, ee: EventEmitter) -> None:
                self1.ee = ee
                self.ee = ee
                self1._on()
        return LazyEventClass
    
    def _on(self) -> None:
        for event in self.onTarget:
            self.ee.on(event, self.onTarget[event])
    
    def on(self, event: str) -> Callable:
        def on_decorator(func: Callable, *args: Any) -> Callable:
            def _impl(*args: Any, **kwargs: Any) -> None:
                func(self.instance, *args, **kwargs)
            if not self.ee:
                self.onTarget[event] = _impl
            else:
                self.ee.on(event, _impl)
            return _impl
        return on_decorator
