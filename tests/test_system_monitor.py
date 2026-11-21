
from unittest.mock import patch, MagicMock

from monitoring.system_monitor import get_system_metrics


@patch("monitoring.system_monitor.psutil.boot_time", return_value=1000)
@patch("monitoring.system_monitor.psutil.disk_usage")
@patch("monitoring.system_monitor.psutil.virtual_memory")
@patch("monitoring.system_monitor.psutil.cpu_percent")
@patch("monitoring.system_monitor.time.time", return_value=2000)
def test_get_system_metrics(
    mock_time,
    mock_cpu,
    mock_memory,
    mock_disk,
    mock_boot,
):
    mock_cpu.return_value = 25.0

    memory = MagicMock()
    memory.percent = 50.0
    memory.available = 512 * 1024 * 1024
    mock_memory.return_value = memory

    disk = MagicMock()
    disk.percent = 40.0
    disk.free = 5 * 1024 ** 3
    mock_disk.return_value = disk

    metrics = get_system_metrics()

    assert metrics["cpu_percent"] == 25.0
    assert metrics["memory_percent"] == 50.0
    assert metrics["memory_available_mb"] == 512.0
    assert metrics["disk_percent"] == 40.0
    assert metrics["disk_free_gb"] == 5.0
    assert metrics["uptime_seconds"] == 1000.0

    assert "timestamp" in metrics
