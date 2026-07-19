import abc
import json

class IPCBase(abc.ABC):
    """
    Abstract Base Class for all IPC mechanisms.
    Defines the standard interface required for sending and receiving data.
    """
    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def connect(self):
        """Connect or initialize resources within the spawned process."""
        pass

    @abc.abstractmethod
    def send(self, data: dict):
        """Send a JSON-serializable dictionary."""
        pass

    @abc.abstractmethod
    def receive(self) -> dict:
        """Receive a dictionary. Should block until data is available."""
        pass

    @abc.abstractmethod
    def teardown(self):
        """Clean up any resources."""
        pass

    def serialize(self, data: dict) -> bytes:
        """Helper to convert dict to bytes."""
        return json.dumps(data).encode('utf-8')

    def deserialize(self, data: bytes) -> dict:
        """Helper to convert bytes to dict."""
        return json.loads(data.decode('utf-8'))
