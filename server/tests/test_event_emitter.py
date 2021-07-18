from app.module.event.deco import EventWrapper
from pymitter import EventEmitter

wrapper = EventWrapper()


@wrapper.lazy_event_on
class TestClass(object):
    def __init__(self) -> None:
        super().__init__()
        self.on_event(EventEmitter())
        print("init")

    @wrapper.on("hi")
    def subscribe(self, data: str) -> None:
        print(f"data:{data}")


# pytest -s test_event_emitter.py
def test() -> None:
    test = TestClass()
    test.ee.emit("hi", "hello")
