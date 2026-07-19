from .base import IPCBase

class QueueIPC(IPCBase):
    def __init__(self, name: str, queue):
        super().__init__(name)
        self.queue = queue

    def connect(self):
        pass

    def send(self, data: dict):
        self.queue.put(data)

    def receive(self) -> dict:
        return self.queue.get()

    def teardown(self):
        pass
