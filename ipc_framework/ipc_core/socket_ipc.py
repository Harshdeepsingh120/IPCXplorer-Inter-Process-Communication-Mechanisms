from .base import IPCBase
import socket
import time

class SocketIPC(IPCBase):
    def __init__(self, name: str, is_sender: bool, host='127.0.0.1', port=65432):
        super().__init__(name)
        self.is_sender = is_sender
        self.host = host
        self.port = port
        self.conn = None
        self.sock = None

    def connect(self):
        if self.is_sender:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connected = False
            while not connected:
                try:
                    self.sock.connect((self.host, self.port))
                    connected = True
                except ConnectionRefusedError:
                    time.sleep(0.5)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.conn, _ = self.sock.accept()

    def send(self, data: dict):
        serialized = self.serialize(data)
        length = len(serialized).to_bytes(4, 'big')
        self.sock.sendall(length + serialized)

    def receive(self) -> dict:
        length_bytes = self.conn.recv(4)
        if not length_bytes:
            raise ConnectionError("Socket closed")
        length = int.from_bytes(length_bytes, 'big')
        
        data = b''
        while len(data) < length:
            packet = self.conn.recv(length - len(data))
            if not packet:
                raise ConnectionError("Socket closed")
            data += packet
            
        return self.deserialize(data)

    def teardown(self):
        try:
            if self.conn:
                self.conn.close()
        except:
            pass
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
