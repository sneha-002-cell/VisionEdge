alerts = []


def add_alert(message):
    alerts.append(message)

    if len(alerts) > 20:
        alerts.pop(0)


def get_alerts():
    return alerts