from .base import IPCBase

class PipeIPC(IPCBase):
    def __init__(self, name: str, conn):
        super().__init__(name)
        self.conn = conn

    def connect(self):
        pass

    def send(self, data: dict):
        self.conn.send(data)

    def receive(self) -> dict:
        return self.conn.recv()

    def teardown(self):
        self.conn.close()
