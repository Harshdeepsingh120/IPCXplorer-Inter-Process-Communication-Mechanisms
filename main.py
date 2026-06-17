import multiprocessing as mp
import threading
import sys
from processes.controller import Controller
from processes.monitor import start_monitor_server

def main():
    monitor_queue = mp.Queue()
    command_queue = mp.Queue()
    
    # Start Controller in a background thread
    controller = Controller(monitor_queue, command_queue)
    controller_thread = threading.Thread(target=controller.run, daemon=True)
    controller_thread.start()
    
    print("Starting Flask Monitor Server on http://localhost:5000")
    print("Press Ctrl+C to exit.")
    
    # Start Flask Server (blocks the main thread)
    try:
        start_monitor_server(monitor_queue, command_queue, port=5000)
    except KeyboardInterrupt:
        print("Shutting down...")
        command_queue.put({"action": "SHUTDOWN"})
        controller_thread.join(timeout=2)
        sys.exit(0)

if __name__ == "__main__":
    main()
