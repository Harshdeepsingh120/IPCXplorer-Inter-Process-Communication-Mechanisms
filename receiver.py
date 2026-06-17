import time
import json
import base64
from .logger import setup_logger

def receiver_process(receiver_id, active_ipc, running_flag, monitor_queue):
    logger = setup_logger(f"Receiver-{receiver_id}", "logs/system.log")
    logger.info(f"Receiver {receiver_id} started using {active_ipc.name}.")

    # Initialize IPC
    active_ipc.connect()

    while running_flag.value:
        try:
            payload = active_ipc.receive()
            recv_time = time.time()
            
            if payload.get("encrypted"):
                decrypted_bytes = base64.b64decode(payload["payload"])
                data = json.loads(decrypted_bytes.decode('utf-8'))
            else:
                data = payload["payload"]
                
            latency = (recv_time - data["timestamp"]) * 1000 # in ms
            
            logger.info(f"Receiver {receiver_id} received msg {data['seq_num']} via {active_ipc.name}. Latency: {latency:.2f}ms")
            
            if monitor_queue:
                monitor_queue.put({
                    "type": "receiver_metric",
                    "receiver_id": receiver_id,
                    "sender_id": data["sender_id"],
                    "ipc_name": active_ipc.name,
                    "seq_num": data["seq_num"],
                    "latency_ms": latency,
                    "priority": data["priority"],
                    "timestamp": recv_time
                })
                
        except Exception as e:
            # If socket closes or queue breaks, we expect an error when tearing down
            if not running_flag.value:
                break
            logger.error(f"Receiver {receiver_id} error: {e}")
            time.sleep(0.5)

    active_ipc.teardown()
    logger.info(f"Receiver {receiver_id} exiting.")
