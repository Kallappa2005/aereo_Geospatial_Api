# Aereo Geospatial File Measurement API

A backend API developed for the Aereo Software Development Engineer Intern assignment.

The application accepts KML files, extracts geospatial features, handles Coordinate Reference Systems (CRS), and calculates measurements such as polygon area and LineString length.

## Tech Stack

- Python 3.12
- FastAPI
- GeoPandas
- Shapely
- PyProj
- SQLAlchemy
- SQLite
- Pytest
- Docker

---

# 1. Setup

## Prerequisites

For local setup:

- Python 3.11+
- uv

For Docker setup:

- Docker Desktop

## Clone the Repository

```bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd aereoGeospetialApi
```

## Run Locally

Install dependencies:

```bash
uv sync
```

Start the application:

```bash
uv run python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run Using Docker

Build the Docker image:

```bash
docker build -t aereo-geospatial-api .
```

Run the container:

```bash
docker run -p 8000:8000 aereo-geospatial-api
```

The API will then be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# 2. API

## POST /api/files/

Uploads and processes a KML file.

### Request

The API accepts a `multipart/form-data` request with a file field named `file`.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@sample_data/sample.kml"
```

### Response

```json
{
    "id": 1,
    "filename": "sample.kml",
    "file_type": "kml",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "status": "COMPLETED"
}
```

---

## GET /api/files/{file_id}/

Returns information about an uploaded file.

### Example

```text
GET /api/files/1/
```

### Response

```json
{
    "id": 1,
    "filename": "sample.kml",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "status": "COMPLETED"
}
```

---

## GET /api/files/{file_id}/measurements/

Returns measurements calculated for the features of an uploaded file.

### Example

```text
GET /api/files/1/measurements/
```

### Response

```json
{
    "file_id": 1,
    "filename": "sample.kml",
    "measurements": [
        {
            "feature_index": 1,
            "geometry_type": "LineString",
            "measurement_type": "length",
            "value": 1085.604,
            "unit": "meters"
        },
        {
            "feature_index": 2,
            "geometry_type": "Polygon",
            "measurement_type": "area",
            "value": 1201684.716,
            "unit": "square_meters"
        }
    ]
}
```

Point features do not have a measurement.

---

# 3. Architecture

```text
aereoGeospetialApi/
│
├── app/
│   ├── main.py
│   ├── routes/
│   │   └── files.py
│   ├── services/
│   │   ├── kml_processor.py
│   │   ├── crs_handler.py
│   │   └── measurement.py
│   └── database/
│       ├── database.py
│       └── models.py
│
├── tests/
│   └── test_files.py
│
├── sample_data/
│   └── sample.kml
│
├── uploads/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

### Main Components

**`routes/files.py`**

Handles file upload, validation, database operations, and API responses.

**`services/kml_processor.py`**

Reads KML files using GeoPandas and extracts features, geometry types, CRS, properties, and measurement information.

**`services/crs_handler.py`**

Transforms geographic coordinates into a suitable projected CRS before measurement calculations.

**`services/measurement.py`**

Calculates measurements based on geometry type.

**`database/`**

Contains the SQLAlchemy database configuration and models.

**`tests/test_files.py`**

Contains the automated API tests using Pytest.

---

# 4. File Processing Flow

```text
KML Upload
    ↓
Validate File
    ↓
Save File
    ↓
Read KML using GeoPandas
    ↓
Extract Features
    ↓
Identify Geometry and CRS
    ↓
Transform CRS if Required
    ↓
Calculate Measurements
    ↓
Store File Information and Measurements
    ↓
Return API Response
```

The processor extracts the feature index, geometry type, geometry, CRS, and properties/attributes from the KML data.

---

# 5. Measurement Calculation

Measurements depend on the geometry type.

### Polygon

```text
Polygon
   ↓
Projected Geometry
   ↓
Area
   ↓
Square Meters
```

### LineString

```text
LineString
   ↓
Projected Geometry
   ↓
Length
   ↓
Meters
```

### Point

Points do not have an area or length measurement, so no measurement is stored for them.

Unsupported measurement geometries are handled without crashing the complete file-processing operation.

---

# 6. CRS Handling

KML coordinates are commonly represented using latitude and longitude.

Calculating area or distance directly using geographic coordinates can produce incorrect results because latitude and longitude are measured in degrees rather than meters.

The application therefore uses the following approach:

```text
Input KML
    ↓
Check CRS
    ↓
Geographic CRS?
    │
    ├── Yes → Estimate suitable UTM CRS
    │           ↓
    │       Transform geometry
    │
    └── No  → Use existing projected CRS
                ↓
          Calculate measurement
```

GeoPandas `estimate_utm_crs()` is used to select a suitable UTM projection based on the location of the input data.

This allows measurements to be calculated in meters and square meters.

---

# 7. Design Decisions

## FastAPI

FastAPI was chosen instead of Django REST Framework because the assignment requires a relatively small REST API and FastAPI provides:

- Simple API development
- Automatic OpenAPI documentation
- Swagger UI
- Easy file upload handling

## GeoPandas

GeoPandas was selected for reading and processing geospatial data and for its integration with Shapely and PyProj.

## CRS Strategy

A dynamic UTM CRS is estimated using `estimate_utm_crs()` instead of using one fixed projected CRS. This makes the approach more suitable for data from different geographic locations.

## SQLite

SQLite was chosen because the assignment is a lightweight backend application and does not require a spatial database.

For a larger production system, PostgreSQL with PostGIS would be a suitable alternative.

## SQLAlchemy

SQLAlchemy provides the database abstraction layer and makes it easier to migrate from SQLite to another relational database in the future.

## Docker

The application was Dockerized so that the application environment and dependencies can be packaged consistently and run without manually configuring the Python environment.

---

# 8. Testing

Two representative Pytest tests are included.

### Test 1 — Successful KML Processing

Verifies that a valid KML file is uploaded and processed successfully with the expected feature count, CRS, and completion status.

### Test 2 — Empty KML Validation

Verifies that an empty KML file is rejected with HTTP 400 and the expected error message.

Run the tests:

```bash
uv run pytest
```

Expected result:

```text
2 passed
```

---

# 9. Current Scope

The current implementation supports KML files.

Supported geometry types:

- Point
- LineString
- Polygon

Supported measurements:

- Polygon → Area
- LineString → Length
- Point → No measurement

Shapefile and ZIP-based Shapefile processing are not currently implemented.

---

# 10. Learning

This project helped me gain practical experience with:

- FastAPI REST API development
- Geospatial data processing using GeoPandas
- Geometry operations using Shapely
- CRS transformation and UTM projections
- SQLAlchemy and SQLite
- File validation and error handling
- Pytest API testing
- Dockerizing a Python application
- Structuring a backend application into routes, services, and database layers

A key learning was understanding why area and distance should not be calculated directly using latitude/longitude coordinates.

---

## Current Scope

- KML file processing (Because Requirements asked either .kml or Shapefile)
- Feature extraction
- CRS-aware measurements
- Polygon area calculation
- LineString length calculation
- REST APIs for file information and measurements

# 11. Future Scope

- Add Shapefile ZIP support for processing `.shp`, `.shx`, `.dbf`, and `.prj` files.
- Add a feature details API to expose geometry type, CRS, properties, and feature information.
- Add geometry-type filtering for measurement results.
- Extend measurements to support MultiPolygon and MultiLineString geometries.
- Add file-level statistics and measurement summaries such as geometry counts, total area, and total length.

---

# 12. Submission

This project was developed as part of the Aereo Software Development Engineer Intern assignment.

GitHub Repository:

```text
https://github.com/Kallappa2005/aereo_Geospatial_Api
```