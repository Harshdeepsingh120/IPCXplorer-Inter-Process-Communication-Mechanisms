let currentIPC = 'PIPE';
const logContainer = document.getElementById('logContainer');
const activeIpcLabel = document.getElementById('active-ipc-label');

const ctx = document.getElementById('latencyChart').getContext('2d');
const latencyChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Latency (ms)',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } },
            x: { grid: { display: false } }
        },
        plugins: { legend: { display: false } },
        animation: { duration: 0 }
    }
});

function switchIPC(ipcName) {
    fetch('/api/switch_ipc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ipc_name: ipcName })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            document.querySelectorAll('.button-group button').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`btn-${ipcName}`).classList.add('active');
            currentIPC = ipcName;
            activeIpcLabel.innerText = ipcName;
            
            latencyChart.data.labels = [];
            latencyChart.data.datasets[0].data = [];
            latencyChart.update();
            
            addLog(`System switching IPC mechanism to ${ipcName}...`, 'high-priority');
        }
    });
}

function addLog(message, type='normal') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString();
    entry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

let lastProcessedTimestamp = 0;

function fetchMetrics() {
    fetch('/api/metrics')
    .then(response => response.json())
    .then(metrics => {
        metrics.forEach(metric => {
            if (metric.timestamp > lastProcessedTimestamp) {
                lastProcessedTimestamp = metric.timestamp;
                
                if (metric.type === 'receiver_metric') {
                    addLog(`Received msg ${metric.seq_num} via ${metric.ipc_name} (Latency: ${metric.latency_ms.toFixed(2)}ms)`, metric.priority === 'HIGH' ? 'high-priority' : 'normal');
                    
                    const timeLabel = new Date(metric.timestamp * 1000).toLocaleTimeString();
                    latencyChart.data.labels.push(timeLabel);
                    latencyChart.data.datasets[0].data.push(metric.latency_ms);
                    
                    if (latencyChart.data.labels.length > 20) {
                        latencyChart.data.labels.shift();
                        latencyChart.data.datasets[0].data.shift();
                    }
                    latencyChart.update();
                } else if (metric.type === 'sender_metric') {
                    addLog(`Sender generated msg ${metric.seq_num} via ${metric.ipc_name}`);
                }
            }
        });
    });
}

setInterval(fetchMetrics, 1000);
