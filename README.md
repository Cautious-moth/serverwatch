# ServerWatch

ServerWatch is a lightweight Python-based system monitoring application that collects system resource metrics, evaluates configurable alert thresholds, and records monitoring data using rotating log files.

## Features

- CPU utilisation monitoring
- Memory utilisation and available memory monitoring
- Disk utilisation and available disk space monitoring
- System uptime tracking
- Configurable alert thresholds
- Threshold-based alerts
- Timestamped application logging
- Rotating log files
- Docker containerisation
- Persistent Docker log storage
- Automated tests with pytest

## Technology Stack

- Python 3.12
- psutil
- pytest
- Docker
- Docker Compose

## Project Structure

```text
serverwatch/
├── config/
│   └── thresholds.py
├── monitoring/
│   ├── alerts.py
│   └── system_monitor.py
├── tests/
│   ├── test_alerts.py
│   └── test_system_monitor.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Configuration

Alert thresholds are defined in `config/thresholds.py`.

| Metric | Default threshold |
|---|---:|
| CPU usage | 80% |
| Memory usage | 80% |
| Disk usage | 80% |

An alert is generated when a metric reaches or exceeds its configured threshold.

## Local Development

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
python -m pytest -v
```

Run the application:

```bash
python -m monitoring.system_monitor
```

Stop monitoring with `Ctrl+C`.

## Docker Deployment

Build and start:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Inspect the metrics log:

```bash
docker compose exec serverwatch sh -c "tail -n 20 /app/logs/system_metrics.log"
```

Stop the application:

```bash
docker compose down
```

## Logging

The application uses Python's rotating file handler.

- Maximum log file size: 1 MB
- Backup files retained: 3
- Log level: INFO
- Threshold violations are recorded as warnings.

## Notes

When running inside Docker, psutil reports metrics visible from the container environment. Host-level monitoring requires appropriate host resource access and configuration.

## Testing

The test suite covers CPU, memory and disk threshold alerts, simultaneous threshold violations, normal operating conditions, threshold boundaries and system metrics collection.