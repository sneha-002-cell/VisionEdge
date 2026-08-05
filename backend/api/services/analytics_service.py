# ============================================
# VisionEdge Analytics Service
# Stores live analytics data in memory
# ============================================

# Shared analytics data
analytics_data = {
    "fps": 0.0,
    "people": 0,
    "cars": 0,
    "buses": 0,
    "motorcycles": 0,
    "line_crossings": 0,
}


def update(data: dict):
    """
    Update live analytics values.
    """
    analytics_data.update(data)


def get():
    """
    Return current analytics.
    """
    return analytics_data.copy()


def get_analytics():
    """
    Compatibility function used by API routes.
    """
    return get()


def reset():
    """
    Reset analytics to default values.
    """
    analytics_data.update({
        "fps": 0.0,
        "people": 0,
        "cars": 0,
        "buses": 0,
        "motorcycles": 0,
        "line_crossings": 0,
    })