# ============================================
# VisionEdge Analytics Service
# Stores live analytics data in memory
# ============================================


DEFAULT_ANALYTICS = {
    "fps": 0.0,
    "people": 0,
    "cars": 0,
    "buses": 0,
    "motorcycles": 0,
    "line_crossings": 0,
}


# Shared live analytics data
analytics_data = DEFAULT_ANALYTICS.copy()


def update(data: dict):
    """
    Update live analytics values.
    """

    if not isinstance(data, dict):
        return

    analytics_data.update(data)


def get():
    """
    Return a copy of the current analytics.
    """

    return analytics_data.copy()


def get_analytics():
    """
    Compatibility function used by the API route.
    """

    return get()


def reset():
    """
    Reset analytics to default values.
    """

    analytics_data.clear()

    analytics_data.update(
        DEFAULT_ANALYTICS
    )