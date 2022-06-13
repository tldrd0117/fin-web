from typing import Callable


class eventManage(object):
    cb = {}
    def on(self, key: str, func: Callable):
        if key not in self.cb:
            self.cb[key] = []
        self.cb[key].append(func)
        print("eventManageOn")
        print(self.cb[key])

    async def emit(self, key: str, *args, **kwargs):
        print(self.cb[key])
        if key in self.cb:
            for func in self.cb[key]:
                await func(*args, **kwargs)
    def off(self, key: str):
        del self.cb[key]
        