#!/usr/bin/env bash

set -euo pipefail

CONTAINER_NAME="serverwatch"
STATE_DIR="/var/lib/serverwatch-recovery"
LAST_RESTART_FILE="$STATE_DIR/last_restart"
COOLDOWN_SECONDS=300

# Read the current Docker health status.
STATUS=$(docker inspect \
    --format='{{.State.Health.Status}}' \
    "$CONTAINER_NAME" 2>/dev/null || true)

# Do nothing if the container cannot be inspected.
if [[ -z "$STATUS" ]]; then
    logger -t serverwatch-recovery \
        "Container $CONTAINER_NAME not found or unavailable"
    exit 0
fi

case "$STATUS" in
    healthy)
        exit 0
        ;;

    starting)
        # Give the application time to initialize.
        exit 0
        ;;

    unhealthy)
        logger -t serverwatch-recovery \
            "Container $CONTAINER_NAME is unhealthy"
        ;;

    *)
        logger -t serverwatch-recovery \
            "Unknown container health status: $STATUS"
        exit 0
        ;;
esac

# Prevent repeated restart attempts.
mkdir -p "$STATE_DIR"

NOW=$(date +%s)
LAST_RESTART=0

if [[ -f "$LAST_RESTART_FILE" ]]; then
    LAST_RESTART=$(cat "$LAST_RESTART_FILE")
fi

ELAPSED=$((NOW - LAST_RESTART))

if (( ELAPSED < COOLDOWN_SECONDS )); then
    logger -t serverwatch-recovery \
        "Restart cooldown active. Skipping recovery."
    exit 0
fi

# Restart the unhealthy container.
logger -t serverwatch-recovery \
    "Restarting unhealthy container $CONTAINER_NAME"

docker restart --time 10 "$CONTAINER_NAME"

# Record successful restart time.
printf '%s\n' "$NOW" > "$LAST_RESTART_FILE"

logger -t serverwatch-recovery \
    "Container $CONTAINER_NAME restarted successfully"
