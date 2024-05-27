from threading import Lock


class MutexManager:
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            self.locks = {}
            cls._init = True

    def get(self, name) -> Lock:
        if name not in self.locks:
            self.locks[name] = Lock()
        return self.locks[name]
