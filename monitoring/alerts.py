
from config.thresholds import THRESHOLDS


def check_thresholds(metrics):
    """Check system metrics against configured thresholds."""

    alerts = []

    for metric, threshold in THRESHOLDS.items():
        value = metrics.get(metric)

        if value is None:
            continue

        if value >= threshold:
            alerts.append({
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "message": (
                    f"WARNING: {metric} is {value}%, "
                    f"exceeding threshold of {threshold}%"
                ),
            })

    return alerts
