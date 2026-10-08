import xml.etree.ElementTree as ET

import geopandas as gpd


def process_kml(file_path: str) -> list[dict]:
    """
    Read a KML file and extract its geospatial features.
    """

    # First, check whether the file is valid XML.
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as exc:
        raise ValueError("Unable to read the KML file.") from exc

    # KML uses this namespace.
    namespace = {
        "kml": "http://www.opengis.net/kml/2.2"
    }

    # Check whether the KML contains any Placemark/features.
    placemarks = root.findall(".//kml:Placemark", namespace)

    if not placemarks:
        raise ValueError("The KML file contains no features.")

    # Now let GeoPandas read the KML.
    try:
        gdf = gpd.read_file(file_path)
    except Exception as exc:
        raise ValueError("Unable to read the KML file.") from exc

    if gdf.empty:
        raise ValueError("The KML file contains no features.")

    if gdf.crs is None:
        raise ValueError("The KML file does not contain a CRS.")

    original_crs = str(gdf.crs)

    from app.services.crs_handler import project_geodataframe
    from app.services.measurement import calculate_measurement

    projected_gdf = project_geodataframe(gdf)

    features = []

    for index, row in gdf.iterrows():
        geometry = row.geometry

        if geometry is None or geometry.is_empty:
            measurement = None
        else:
            projected_geometry = projected_gdf.iloc[index].geometry
            measurement = calculate_measurement(projected_geometry)

        properties = {
            column: row[column]
            for column in gdf.columns
            if column != "geometry"
        }

        features.append(
            {
                "feature_index": index,
                "geometry_type": (
                    geometry.geom_type
                    if geometry is not None
                    else None
                ),
                "geometry": geometry,
                "crs": original_crs,
                "properties": properties,
                "measurement": measurement,
            }
        )

    return features