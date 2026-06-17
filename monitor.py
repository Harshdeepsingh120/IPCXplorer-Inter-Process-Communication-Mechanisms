from flask import Flask, send_from_directory, jsonify, request
import threading
import queue

def start_monitor_server(monitor_queue, command_queue, port=5000):
    app = Flask(__name__, static_folder='../frontend')
    
    recent_metrics = []
    MAX_METRICS = 100
    
    def process_queue():
        while True:
            try:
                metric = monitor_queue.get(timeout=0.1)
                recent_metrics.append(metric)
                if len(recent_metrics) > MAX_METRICS:
                    recent_metrics.pop(0)
            except queue.Empty:
                pass
            except Exception:
                break
                
    q_thread = threading.Thread(target=process_queue, daemon=True)
    q_thread.start()

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory(app.static_folder, path)

    @app.route('/api/metrics')
    def get_metrics():
        return jsonify(recent_metrics)

    @app.route('/api/switch_ipc', methods=['POST'])
    def switch_ipc():
        data = request.json
        ipc_name = data.get('ipc_name')
        if ipc_name in ["PIPE", "MESSAGE_QUEUE", "SHARED_MEMORY", "SOCKET"]:
            command_queue.put({"action": "SWITCH_IPC", "ipc_name": ipc_name})
            return jsonify({"status": "success", "message": f"Switching to {ipc_name}"})
        return jsonify({"status": "error", "message": "Invalid IPC mechanism"}), 400

    app.run(host='0.0.0.0', port=port, use_reloader=False)
