import time
import multiprocessing as mp
from multiprocessing.shared_memory import SharedMemory
import queue

from ipc_core.pipe_ipc import PipeIPC
from ipc_core.queue_ipc import QueueIPC
from ipc_core.shm_ipc import ShmIPC
from ipc_core.socket_ipc import SocketIPC

from .sender import sender_process
from .receiver import receiver_process
from .logger import setup_logger

logger = setup_logger("Controller", "logs/system.log")

class Controller:
    def __init__(self, monitor_queue, command_queue):
        self.monitor_queue = monitor_queue
        self.command_queue = command_queue
        
        self.current_ipc_name = "PIPE" # default
        self.running = True
        
        self.sender_procs = []
        self.receiver_procs = []
        
        self.shm = None

    def setup_ipc_objects(self, ipc_name):
        """Creates the necessary IPC objects for sender and receiver."""
        if ipc_name == "PIPE":
            recv_conn, send_conn = mp.Pipe(duplex=False)
            sender_ipc = PipeIPC("PIPE", send_conn)
            receiver_ipc = PipeIPC("PIPE", recv_conn)
            return sender_ipc, receiver_ipc
            
        elif ipc_name == "MESSAGE_QUEUE":
            q = mp.Queue()
            sender_ipc = QueueIPC("MESSAGE_QUEUE", q)
            receiver_ipc = QueueIPC("MESSAGE_QUEUE", q)
            return sender_ipc, receiver_ipc
            
        elif ipc_name == "SHARED_MEMORY":
            try:
                self.shm = SharedMemory(name="ipc_shm", create=True, size=1024*1024)
            except FileExistsError:
                self.shm = SharedMemory(name="ipc_shm")
            
            lock = mp.Lock()
            write_event = mp.Event()
            read_event = mp.Event()
            read_event.set() # allow sender to write first
            
            sender_ipc = ShmIPC("SHARED_MEMORY", "ipc_shm", lock, write_event, read_event)
            receiver_ipc = ShmIPC("SHARED_MEMORY", "ipc_shm", lock, write_event, read_event)
            return sender_ipc, receiver_ipc
            
        elif ipc_name == "SOCKET":
            sender_ipc = SocketIPC("SOCKET", is_sender=True, host='127.0.0.1', port=65432)
            receiver_ipc = SocketIPC("SOCKET", is_sender=False, host='127.0.0.1', port=65432)
            return sender_ipc, receiver_ipc

    def start_processes(self, ipc_name):
        logger.info(f"Starting processes with {ipc_name}...")
        self.current_ipc_name = ipc_name
        self.proc_running_flag = mp.Value('b', True)
        
        sender_ipc, receiver_ipc = self.setup_ipc_objects(ipc_name)
        
        # Start Receiver first
        r_proc = mp.Process(target=receiver_process, args=(1, receiver_ipc, self.proc_running_flag, self.monitor_queue))
        r_proc.start()
        self.receiver_procs.append(r_proc)
        
        if ipc_name == "SOCKET":
            time.sleep(0.5)
            
        # Start 1 Sender
        s_proc = mp.Process(target=sender_process, args=(1, sender_ipc, self.proc_running_flag, self.monitor_queue, True))
        s_proc.start()
        self.sender_procs.append(s_proc)

    def stop_processes(self):
        logger.info("Stopping current processes...")
        self.proc_running_flag.value = False
        
        # Terminate immediately for rapid switching without hanging
        for p in self.sender_procs + self.receiver_procs:
            if p.is_alive():
                p.terminate()
                p.join()
                
        self.sender_procs.clear()
        self.receiver_procs.clear()
        
        if self.shm:
            self.shm.close()
            try:
                self.shm.unlink()
            except:
                pass
            self.shm = None
            
        logger.info("Processes stopped cleanly.")

    def run(self):
        self.start_processes(self.current_ipc_name)
        
        while self.running:
            try:
                cmd = self.command_queue.get(timeout=0.5)
                if cmd['action'] == 'SWITCH_IPC':
                    new_ipc = cmd['ipc_name']
                    if new_ipc != self.current_ipc_name:
                        logger.info(f"Controller received command to switch IPC to {new_ipc}")
                        self.stop_processes()
                        self.start_processes(new_ipc)
                elif cmd['action'] == 'SHUTDOWN':
                    self.running = False
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Controller error: {e}")
                
        self.stop_processes()
