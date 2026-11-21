
import logging
import time
from logging.handlers import RotatingFileHandler
from monitoring.alerts import check_thresholds
from pathlib import Path
from datetime import datetime

import psutil


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "system_metrics.log"


# Configure rotating logging
logger = logging.getLogger("serverwatch")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,
    backupCount=3
)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_system_metrics():
    """Collect CPU, memory, disk and uptime metrics."""

    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    uptime_seconds = time.time() - psutil.boot_time()

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu_usage,
        "memory_percent": memory.percent,
        "memory_available_mb": round(
            memory.available / (1024 ** 2), 2
        ),
        "disk_percent": disk.percent,
        "disk_free_gb": round(
            disk.free / (1024 ** 3), 2
        ),
        "uptime_seconds": round(uptime_seconds, 2),
    }

    return metrics


def log_metrics(metrics):
    """Write collected metrics to the application log."""

    logger.info(
        "cpu_percent=%.2f memory_percent=%.2f "
        "memory_available_mb=%.2f disk_percent=%.2f "
        "disk_free_gb=%.2f uptime_seconds=%.2f",
        metrics["cpu_percent"],
        metrics["memory_percent"],
        metrics["memory_available_mb"],
        metrics["disk_percent"],
        metrics["disk_free_gb"],
        metrics["uptime_seconds"],
    )



if __name__ == "__main__":
    logger.info("ServerWatch monitoring started")

    try:
        while True:
            metrics = get_system_metrics()
            log_metrics(metrics)

            print(metrics)

            alerts = check_thresholds(metrics)

            for alert in alerts:
                logger.warning(alert["message"])
                print(alert["message"])

            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("ServerWatch monitoring stopped by user")
        print("\nServerWatch stopped successfully.")
