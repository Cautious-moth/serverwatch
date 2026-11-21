
import time

from monitoring import health


def test_missing_heartbeat_is_unhealthy(tmp_path, monkeypatch):
    heartbeat = tmp_path / "serverwatch.heartbeat"
    monkeypatch.setattr(health, "HEARTBEAT_FILE", heartbeat)

    assert health.is_healthy() is False


def test_recent_heartbeat_is_healthy(tmp_path, monkeypatch):
    heartbeat = tmp_path / "serverwatch.heartbeat"
    monkeypatch.setattr(health, "HEARTBEAT_FILE", heartbeat)

    health.record_heartbeat()

    assert heartbeat.exists()
    assert health.is_healthy() is True


def test_stale_heartbeat_is_unhealthy(tmp_path, monkeypatch):
    heartbeat = tmp_path / "serverwatch.heartbeat"
    monkeypatch.setattr(health, "HEARTBEAT_FILE", heartbeat)

    heartbeat.touch()
    stale_time = time.time() - 30
    import os
    os.utime(heartbeat, (stale_time, stale_time))

    assert health.is_healthy(max_age_seconds=20) is False


def test_future_heartbeat_is_unhealthy(tmp_path, monkeypatch):
    heartbeat = tmp_path / "serverwatch.heartbeat"
    monkeypatch.setattr(health, "HEARTBEAT_FILE", heartbeat)

    heartbeat.touch()
    future_time = time.time() + 30
    import os
    os.utime(heartbeat, (future_time, future_time))

    assert health.is_healthy() is False
