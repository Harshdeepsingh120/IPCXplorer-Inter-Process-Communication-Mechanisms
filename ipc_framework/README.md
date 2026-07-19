# Comprehensive Inter-Process Communication (IPC) Framework

This is a complete, presentation-ready project demonstrating 4 major IPC mechanisms, process lifecycle management, synchronization, and real-time visualization.

## Prerequisites
- Python 3.8+
- `pip install flask chart.js` (Chart.js is pulled via CDN, so just Flask is needed locally).

## Installation
1. Open a terminal in this directory.
2. Install dependencies:
   ```bash
   pip install flask
   ```

## Execution Guide

1. Run the main entry point:
   ```bash
   python main.py
   ```
2. Open your web browser and navigate to:
   `http://localhost:5000`

3. **Using the Dashboard:**
   - Observe the live latency chart and real-time logs.
   - Click the **Control Panel** buttons to dynamically switch the active IPC mechanism.
   - Watch the logs for "High Priority" encrypted messages and simulated Sender crashes.

## Directory Structure
- `ipc_core/`: The core abstraction and implementation of Pipes, Queues, Shared Memory, and Sockets.
- `processes/`: The process definitions (Controller, Sender, Receiver, Monitor).
- `frontend/`: The HTML/CSS/JS dashboard.
- `docs/`: Presentation guides and explanations.
- `logs/`: Runtime system logs (`system.log`).
