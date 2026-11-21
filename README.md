# ServerWatch

ServerWatch is a lightweight Python-based Linux server monitoring application designed to collect system resource metrics, detect threshold violations, and automatically recover an unhealthy monitoring container.

The project demonstrates practical DevOps engineering through Python monitoring, automated testing, Docker containerisation, persistent logging, Linux service management, automated recovery, and CI/CD deployment to AWS EC2.

## Features

### System Monitoring
- CPU utilisation monitoring
- Memory utilisation and available memory monitoring
- Disk utilisation and available disk space monitoring
- System uptime tracking
- Periodic metric collection

### Alerting and Logging
- Configurable CPU, memory, and disk alert thresholds
- Threshold-based warning alerts
- Timestamped application logging
- Rotating log files
- Persistent Docker log storage

### Health Monitoring and Recovery
- Application heartbeat tracking
- Docker health checks
- Automated unhealthy-container detection
- Systemd-based recovery watchdog
- Automatic container restart when unhealthy
- Five-minute restart cooldown to prevent repeated restart attempts

### DevOps and Deployment
- Docker and Docker Compose containerisation
- Non-root container execution
- Automated testing with pytest
- GitHub Actions CI pipeline
- Automated deployment to AWS EC2
- Post-deployment Docker health verification

## Architecture

```text
              Developer
                  |
                  v
             GitHub Push
                  |
                  v
           GitHub Actions
                  |
             Run pytest
                  |
             Tests pass?
                  |
                  v
             SSH to EC2
                  |
                  v
          Pull latest code
                  |
                  v
        Docker Compose Build
                  |
                  v
          ServerWatch Container
                  |
          +-------+-------+
          |               |
          v               v
     Collect Metrics   Record Heartbeat
          |               |
          v               v
     Evaluate Alerts  Docker Health Check
          |               |
          v               v
     Write Logs       Container Health
                          |
                          v
                 Systemd Recovery Timer
                          |
                          v
                 Check Every 30 Seconds
                          |
                 Is container unhealthy?
                     /          \
                   Yes           No
                    |             |
                    v             v
              Restart Docker    No Action
                Container
```

The application runs inside Docker, while a systemd timer on the EC2 host independently monitors container health and performs recovery when necessary.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Monitoring application |
| psutil | System resource metrics |
| pytest | Automated testing |
| Docker | Application containerisation |
| Docker Compose | Container lifecycle management |
| Linux systemd | Automated recovery scheduling |
| Bash | Recovery automation |
| Git and GitHub | Version control |
| GitHub Actions | CI/CD automation |
| AWS EC2 | Cloud deployment |

## Project Structure

```text
serverwatch/
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   └── thresholds.py
├── monitoring/
│   ├── alerts.py
│   ├── health.py
│   └── system_monitor.py
├── scripts/
│   ├── recover_unhealthy.sh
│   └── systemd/
│       ├── serverwatch-recovery.service
│       └── serverwatch-recovery.timer
├── tests/
│   ├── test_alerts.py
│   ├── test_health.py
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
| CPU utilisation | 80% |
| Memory utilisation | 80% |
| Disk utilisation | 80% |

An alert is generated when a monitored metric reaches or exceeds its configured threshold.

## Local Development

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run automated tests:

```bash
python -m pytest -v
```

Run the monitoring application:

```bash
python -m monitoring.system_monitor
```

Stop monitoring with `Ctrl+C`.

## Docker Deployment

Build and start the application:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Inspect the metrics log:

```bash
docker compose exec serverwatch \
  sh -c "tail -n 20 /app/logs/system_metrics.log"
```

Stop the application:

```bash
docker compose down
```

The application uses a Docker named volume to preserve logs independently of the container lifecycle.

## Health Monitoring

ServerWatch uses an application heartbeat mechanism to determine whether monitoring cycles are completing successfully.

After a successful monitoring cycle, the application updates its heartbeat file.

The Docker health check executes:

```bash
python -m monitoring.health
```

The health checker evaluates the age of the most recent heartbeat.

A heartbeat older than 20 seconds is considered unhealthy.

The Docker health check is configured with:

- Check interval: 10 seconds
- Timeout: 5 seconds
- Start period: 15 seconds
- Failure retries: 3

This allows Docker to identify situations where the container is still running but its monitoring process has stopped making progress.

## Automated Container Recovery

ServerWatch uses a host-level systemd watchdog to recover unhealthy containers.

The recovery mechanism consists of:

1. A systemd timer triggers the recovery service every 30 seconds.
2. The recovery script checks the Docker container health status.
3. Healthy and starting containers are left untouched.
4. An unhealthy container triggers a recovery attempt.
5. A five-minute cooldown prevents repeated restart attempts.
6. Docker restarts the container, allowing monitoring to resume.

The recovery script is installed on the EC2 host at:

```text
/usr/local/bin/serverwatch-recovery
```

The systemd service and timer are installed under:

```text
/etc/systemd/system/serverwatch-recovery.service
/etc/systemd/system/serverwatch-recovery.timer
```

Check recovery timer status:

```bash
sudo systemctl status serverwatch-recovery.timer
```

Check whether the timer is enabled:

```bash
sudo systemctl is-enabled serverwatch-recovery.timer
```

Inspect recovery events:

```bash
sudo journalctl -t serverwatch-recovery
```

### Recovery Testing

The recovery mechanism was tested on the deployed EC2 instance using a controlled failure scenario.

The monitoring process was temporarily suspended using `SIGSTOP`, allowing the Docker health check to detect a stale heartbeat.

The recovery watchdog subsequently detected the unhealthy container and restarted it.

The test confirmed:

- Docker transitioned the container to an unhealthy state.
- The systemd recovery service detected the failure.
- The recovery script executed a container restart.
- A new monitoring process started.
- The container returned to a healthy state.

Recovery events were verified through the system journal, and the final Docker health status was `healthy`.

## Continuous Integration and Deployment

ServerWatch uses GitHub Actions to automate testing and deployment.

The workflow is defined in:

```text
.github/workflows/ci.yml
```

### Continuous Integration

On pushes and pull requests targeting `main`, GitHub Actions:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs development dependencies.
4. Runs the pytest test suite.

### Continuous Deployment

On successful pushes to `main`, the deployment job:

1. Connects securely to the EC2 instance using SSH.
2. Pulls the latest application code.
3. Rebuilds and starts the Docker Compose application.
4. Waits for the Docker health check.
5. Reports deployment success only after the container becomes healthy.

The deployment uses GitHub repository secrets:

| Secret | Purpose |
|---|---|
| `EC2_HOST` | EC2 public hostname |
| `EC2_USER` | EC2 SSH username |
| `EC2_SSH_KEY` | Private deployment SSH key |

Credentials are stored in GitHub Secrets rather than committed to the repository.

## Logging

The application uses Python's rotating file handler.

| Setting | Value |
|---|---|
| Maximum log file size | 1 MB |
| Backup files retained | 3 |
| Log level | INFO |
| Threshold violations | WARNING |

Logs are stored in the Docker-mounted `/app/logs` directory and persist through container recreation.

Recovery events are additionally recorded in the Linux system journal.

## Testing

The automated test suite covers:

- CPU, memory, and disk threshold alerts
- Simultaneous threshold violations
- Normal operating conditions
- Threshold boundary conditions
- System metrics collection
- Missing heartbeat detection
- Recent heartbeat validation
- Stale heartbeat detection
- Future heartbeat timestamp handling

The current test suite contains **11 automated tests**, which pass locally and in the GitHub Actions CI pipeline.

## Deployment Environment

The application has been deployed to an AWS EC2 instance running Amazon Linux 2023.

The deployment environment includes:

- Docker Engine
- Docker Compose
- Git
- Python-based application container
- systemd recovery timer and service
- GitHub Actions SSH deployment

## Notes and Limitations

- When running inside Docker, `psutil` reports metrics visible from the container environment. Host-level monitoring requires appropriate host resource access and configuration.
- The recovery watchdog monitors the ServerWatch container. It does not independently recover the EC2 instance or an unavailable Docker daemon.
- The restart cooldown limits repeated recovery attempts but does not replace alerting or incident investigation.
- GitHub Actions deployment depends on EC2 availability, SSH connectivity, and successful container health verification.

## Project Objectives

ServerWatch demonstrates practical experience in:

- Python application development
- Linux system administration
- Resource monitoring and alerting
- Docker containerisation
- Automated health checks
- Bash scripting and systemd
- Failure detection and automated recovery
- Automated software testing
- Git-based development workflows
- CI/CD pipeline implementation
- AWS EC2 deployment
