from shapely.geometry import Point, LineString, Polygon


def calculate_measurement(geometry):
    """
    Calculate measurement based on geometry type.
    """

    if geometry is None:
        return None

    if isinstance(geometry, Polygon):
        return {
            "measurement_type": "area",
            "value": geometry.area,
            "unit": "square_meters",
        }

    if isinstance(geometry, LineString):
        return {
            "measurement_type": "length",
            "value": geometry.length,
            "unit": "meters",
        }

    if isinstance(geometry, Point):
        return None

    return None