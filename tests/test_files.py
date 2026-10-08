from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

SAMPLE_KML = Path("sample_data/sample.kml")


def test_upload_valid_kml():
    with open(SAMPLE_KML, "rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "sample.kml",
                    file,
                    "application/vnd.google-earth.kml+xml",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample.kml"
    assert data["feature_count"] == 3
    assert data["crs"] == "EPSG:4326"
    assert data["status"] == "COMPLETED"


def test_upload_empty_kml():
    empty_kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
</kml>
"""

    response = client.post(
        "/api/files/",
        files={
            "file": (
                "empty.kml",
                empty_kml.encode("utf-8"),
                "application/vnd.google-earth.kml+xml",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "The KML file contains no features."