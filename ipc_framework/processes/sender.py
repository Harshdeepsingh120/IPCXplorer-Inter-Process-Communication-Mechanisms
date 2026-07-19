import time
import json
import random
import base64
from .logger import setup_logger

def sender_process(sender_id, active_ipc, running_flag, monitor_queue, simulate_crash=False):
    logger = setup_logger(f"Sender-{sender_id}", "logs/system.log")
    logger.info(f"Sender {sender_id} started using {active_ipc.name}.")

    # Initialize IPC
    active_ipc.connect()

    seq_num = 0
    while running_flag.value:
        try:
            # Simulate Crash
            if simulate_crash and random.random() < 0.05:
                logger.warning(f"Sender {sender_id} experienced a simulated crash!")
                time.sleep(2)
                logger.info(f"Sender {sender_id} restarted after crash.")

            # Generate simulated sensor data
            data = {
                "sender_id": sender_id,
                "seq_num": seq_num,
                "temperature": round(random.uniform(20.0, 35.0), 2),
                "humidity": round(random.uniform(40.0, 60.0), 2),
                "priority": "HIGH" if random.random() < 0.2 else "NORMAL",
                "timestamp": time.time(),
                "ipc_name": active_ipc.name
            }
            
            # Basic Encryption simulation for HIGH priority
            if data["priority"] == "HIGH":
                raw_str = json.dumps(data)
                encrypted = base64.b64encode(raw_str.encode('utf-8')).decode('utf-8')
                payload = {"encrypted": True, "payload": encrypted}
            else:
                payload = {"encrypted": False, "payload": data}
            
            active_ipc.send(payload)
            logger.info(f"Sender {sender_id} sent msg {seq_num} via {active_ipc.name}")
            
            if monitor_queue:
                monitor_queue.put({
                    "type": "sender_metric",
                    "sender_id": sender_id,
                    "ipc_name": active_ipc.name,
                    "seq_num": seq_num,
                    "timestamp": data["timestamp"]
                })
                
            seq_num += 1
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Sender {sender_id} error: {e}")
            time.sleep(1)

    active_ipc.teardown()
    logger.info(f"Sender {sender_id} exiting.")
