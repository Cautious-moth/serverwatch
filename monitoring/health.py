
import sys
import tempfile
import time
from pathlib import Path


HEARTBEAT_FILE = (
    Path(tempfile.gettempdir()) / "serverwatch.heartbeat"
)

MAX_HEARTBEAT_AGE_SECONDS = 20


def record_heartbeat():
    """Record that a monitoring cycle completed successfully."""
    HEARTBEAT_FILE.touch()


def is_healthy(max_age_seconds=MAX_HEARTBEAT_AGE_SECONDS):
    """Return whether the latest heartbeat is recent."""

    if not HEARTBEAT_FILE.exists():
        return False

    heartbeat_age = time.time() - HEARTBEAT_FILE.stat().st_mtime

    return 0 <= heartbeat_age <= max_age_seconds


if __name__ == "__main__":
    if is_healthy():
        print("ServerWatch status: healthy")
        sys.exit(0)

    print("ServerWatch status: unhealthy")
    sys.exit(1)
