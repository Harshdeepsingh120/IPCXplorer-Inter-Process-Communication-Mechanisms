from .base import IPCBase

class ShmIPC(IPCBase):
    def __init__(self, name: str, shm_name: str, lock, write_event, read_event):
        super().__init__(name)
        self.shm_name = shm_name
        self.lock = lock
        self.write_event = write_event
        self.read_event = read_event
        self.shm = None

    def connect(self):
        from multiprocessing.shared_memory import SharedMemory
        self.shm = SharedMemory(name=self.shm_name)

    def send(self, data: dict):
        serialized = self.serialize(data)
        size = len(serialized)
        
        with self.lock:
            self.shm.buf[:4] = size.to_bytes(4, 'big')
            self.shm.buf[4:4+size] = serialized
            
        self.write_event.set()
        # Wait for receiver to read before we can send the next one
        self.read_event.wait()
        self.read_event.clear()

    def receive(self) -> dict:
        # Wait for sender to write
        self.write_event.wait()
        
        with self.lock:
            size = int.from_bytes(self.shm.buf[:4], 'big')
            serialized = bytes(self.shm.buf[4:4+size])
            
        self.write_event.clear()
        # Notify sender we have read it
        self.read_event.set()
        
        return self.deserialize(serialized)

    def teardown(self):
        if self.shm:
            self.shm.close()
