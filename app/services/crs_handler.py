import geopandas as gpd


def project_geodataframe(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Transform geographic coordinates into a projected CRS
    suitable for distance and area measurements.
    """

    if gdf.crs is None:
        raise ValueError("Input data has no CRS.")

    if not gdf.crs.is_geographic:
        return gdf

    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    return gdf.to_crs(projected_crs)