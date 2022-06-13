
from typing import Any, Awaitable, Callable

from .events import eventManage

def makeRegisteringDecorator(foreignDecorator):
    def newDecorator(func):
        # Call to newDecorator(method)
        # Exactly like old decorator, but output keeps track of what decorated it
        R = foreignDecorator(func) # apply foreignDecorator, like call to foreignDecorator(method) would have done
        R.decorator = newDecorator # keep track of decorator
        R.ID_DECO = id(newDecorator)
        #R.original = func         # might as well keep track of everything!
        return R

    newDecorator.__name__ = foreignDecorator.__name__
    newDecorator.__doc__ = foreignDecorator.__doc__
    # (*)We can be somewhat "hygienic", but newDecorator still isn't signature-preserving, i.e. you will not be able to get a runtime list of parameters. For that, you need hackish libraries...but in this case, the only argument is func, so it's not a big issue

    return newDecorator


def methodsWithDecorator(cls, decorator):
    """ 
        Returns all methods in CLS with DECORATOR as the
        outermost decorator.

        DECORATOR must be a "registering decorator"; one
        can make any decorator "registering" via the
        makeRegisteringDecorator function.
    """
    for maybeDecorated in cls.__dict__.values():
        if hasattr(maybeDecorated, 'decorator'):
            if maybeDecorated.decorator == decorator:
                return maybeDecorated

class EventEmitter(object):
    def __init__(self, instance, em) -> None:
        self.instance: Any = instance
        self.em: eventManage = em
    
    def on(self, key, func):
        self.em.on(key, func)
    
    async def emit(self, key, *args, **kwargs ):
        if self.instance.__class__ is None or self.instance.__class__.__name__ is None:
            return
        eventKey = str(id(self.instance)) + str(id(self))
        await self.em.emit(eventKey+key, *args, **kwargs)



class eventsDecorator:
    events = {}
    classes = set()
    eventManages = {}
    @staticmethod
    def on(eventName: str):
        def decorator(func: Awaitable):
            return func
        newDeco = makeRegisteringDecorator(decorator)
        eventsDecorator.events[eventName] = newDeco
        return newDeco
    
    @staticmethod
    async def emit(instance: Any, ee: eventManage, key, *args, **kwargs ):
        if instance.__class__ is None or instance.__class__.__name__ is None:
            return
        eventKey = str(id(instance)) + str(id(ee))
        await ee.emit(eventKey+key, *args, **kwargs)
    
    @staticmethod
    def makeEmitter(instance: Any):
        return EventEmitter(instance, eventManage())


    @staticmethod
    def register(instance: Any, ee: EventEmitter):
        if instance.__class__ is None or instance.__class__.__name__ is None:
            return
        eventKey = str(id(instance)) + str(id(ee))
        
        if eventKey not in eventsDecorator.classes:
            eventsDecorator.classes.add(eventKey)
        else:
            return
        keys = eventsDecorator.events.keys()
        for key in keys:
            func = methodsWithDecorator(instance.__class__, eventsDecorator.events[key])
            print(func)
            if func is None:
                continue
            func = getattr(instance, func.__name__)
            print("onEvent:"+eventKey+key+" func:"+str(func))
            ee.on(eventKey + key, func)
        return keys
    
    
    @staticmethod
    def unregist(instance: Any, ee: EventEmitter):
        eventKey = str(id(instance)) + str(id(ee))
        if eventKey in eventsDecorator.classes:
            eventsDecorator.classes.remove(eventKey)
        keys = eventsDecorator.events.keys()
        for key in keys:
            func = methodsWithDecorator(instance.__class__, eventsDecorator.events[key])
            if func is None:
                continue
            func = getattr(instance, func.__name__)
            ee.off(eventKey + key)
    
