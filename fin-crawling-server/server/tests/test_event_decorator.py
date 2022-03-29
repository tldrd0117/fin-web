from app.util.decorator import eventsDecorator
from pymitter import EventEmitter


class Target(object):
    def __init__(self) -> None:
        self.ee = EventEmitter()
        eventsDecorator.register(self, self.ee)
    
    @eventsDecorator.on("click")
    def test(self, data):
        print("isitTest")
        print(self)
        print(data)

# pytest -s test_event_decorator.py
def test() -> None:
    target = Target()
    target.ee.emit("click", "values")
    print("emit")
