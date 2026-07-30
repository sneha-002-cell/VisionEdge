# Shared analytics data

analytics_data = {
    "fps": 0,
    "people": 0,
    "cars": 0,
    "buses": 0,
    "motorcycles": 0,
    "line_crossings": 0
}


def update(data):
    analytics_data.update(data)


def get():
    return analytics_data