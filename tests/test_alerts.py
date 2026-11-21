
from monitoring.alerts import check_thresholds


def test_cpu_threshold_exceeded():
    metrics = {
        "cpu_percent": 90,
        "memory_percent": 40,
        "disk_percent": 20,
    }

    alerts = check_thresholds(metrics)

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "cpu_percent"


def test_memory_threshold_exceeded():
    metrics = {
        "cpu_percent": 20,
        "memory_percent": 90,
        "disk_percent": 20,
    }

    alerts = check_thresholds(metrics)

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "memory_percent"


def test_disk_threshold_exceeded():
    metrics = {
        "cpu_percent": 20,
        "memory_percent": 30,
        "disk_percent": 90,
    }

    alerts = check_thresholds(metrics)

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "disk_percent"


def test_no_alerts_when_metrics_are_normal():
    metrics = {
        "cpu_percent": 20,
        "memory_percent": 30,
        "disk_percent": 40,
    }

    alerts = check_thresholds(metrics)

    assert alerts == []


def test_multiple_thresholds_exceeded():
    metrics = {
        "cpu_percent": 90,
        "memory_percent": 85,
        "disk_percent": 95,
    }

    alerts = check_thresholds(metrics)

    assert len(alerts) == 3


def test_exact_threshold_triggers_alert():
    metrics = {
        "cpu_percent": 80,
        "memory_percent": 30,
        "disk_percent": 40,
    }

    alerts = check_thresholds(metrics)

    assert len(alerts) == 1
    assert alerts[0]["value"] == 80
