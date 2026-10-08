# Aereo Geospatial File Measurement API

A backend API built for the Aereo Software Development Engineer Intern assignment.

The application accepts KML files, extracts their geospatial features, handles Coordinate Reference Systems (CRS), and calculates measurements such as polygon area and LineString length.

## Tech Stack

- Python 3.12
- FastAPI
- GeoPandas
- Shapely
- PyProj
- SQLAlchemy
- SQLite
- Pytest
- Uvicorn

---

# 1. Setup

## Prerequisites

Make sure the following are installed:

- Python 3.11+
- uv

## Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd aereoGeospetialApi
```

## Install dependencies

```bash
uv sync
```

## Run the application

```bash
uv run python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 2. API

## POST /api/files/

Uploads and processes a KML file.

### Request

Use `multipart/form-data` with a file field named `file`.

Example using curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@sample_data/sample.kml"
```

### Successful Response

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

The uploaded file is processed immediately and its measurements are stored in the database.

---

## GET /api/files/{file_id}/

Returns information about a previously uploaded file.

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

### File Not Found

```json
{
    "detail": "File not found."
}
```

---

## GET /api/files/{file_id}/measurements/

Returns the measurements calculated for the features of a file.

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

Point features do not have a measurement and are therefore not included in the measurements list.

---

# 3. Validation and Error Handling

The API validates uploaded files before processing them.

### Unsupported File Type

Only KML files are currently supported.

```json
{
    "detail": "Only KML files are supported."
}
```

### Invalid KML

If the uploaded file cannot be parsed as valid KML/XML:

```json
{
    "detail": "Unable to read the KML file."
}
```

### Empty KML

If the KML is valid but contains no features:

```json
{
    "detail": "The KML file contains no features."
}
```

### File Not Found

If the requested file ID does not exist:

```json
{
    "detail": "File not found."
}
```

---

# 4. Architecture

## Application Structure

```text
aereoGeospetialApi/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── files.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kml_processor.py
│   │   ├── crs_handler.py
│   │   └── measurement.py
│   │
│   └── database/
│       ├── __init__.py
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
├── aereo.db
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

### Responsibilities

#### `main.py`

Creates the FastAPI application, initializes the database tables, and registers the API routes.

#### `routes/files.py`

Handles:

- File upload
- File validation
- Database operations
- Processing errors
- API responses

#### `services/kml_processor.py`

Handles KML processing using GeoPandas.

It extracts:

- Feature index
- Geometry type
- Geometry
- CRS
- Properties/attributes
- Measurement information

#### `services/crs_handler.py`

Handles coordinate reference system transformations.

It transforms geographic coordinates into a suitable projected CRS before calculating metric measurements.

#### `services/measurement.py`

Calculates measurements based on geometry type.

- Polygon → Area
- LineString → Length
- Point → No measurement

#### `database/database.py`

Creates the SQLAlchemy database engine and database session.

#### `database/models.py`

Defines the database models used to store uploaded file information and measurements.

#### `tests/test_files.py`

Contains the automated Pytest tests for the main application flows.

---

# 5. File Processing Flow

The file processing flow is:

```text
Client
  │
  │ POST /api/files/
  ▼
FastAPI Route
  │
  ├── Validate filename
  │
  ├── Save uploaded KML
  │
  ▼
KML Processor
  │
  ├── Validate KML/XML
  ├── Check for features
  ├── Read using GeoPandas
  ├── Extract geometry
  ├── Extract properties
  └── Identify CRS
  │
  ▼
CRS Handler
  │
  └── Transform geographic CRS
      to projected CRS when required
  │
  ▼
Measurement Service
  │
  ├── Polygon → Area
  ├── LineString → Length
  └── Point → No measurement
  │
  ▼
SQLite Database
  │
  ├── File information
  └── Measurements
```

---

# 6. Measurement Calculation Flow

The application determines the measurement based on the geometry type.

## Polygon

For polygon geometries:

```text
Polygon
   ↓
Projected geometry
   ↓
geometry.area
   ↓
Area in square meters
```

## LineString

For LineString geometries:

```text
LineString
   ↓
Projected geometry
   ↓
geometry.length
   ↓
Length in meters
```

## Point

Points do not have an area or length measurement, so the application returns no measurement for them.

Unsupported geometry types are also handled without crashing the complete file-processing operation.

---

# 7. CRS Handling

KML coordinates are commonly represented using geographic coordinates such as latitude and longitude.

Directly calculating:

```text
geometry.area
geometry.length
```

on latitude/longitude coordinates can produce incorrect measurements because degrees are angular units rather than metric units.

Therefore, the application follows this approach:

```text
Input KML
   ↓
Check CRS
   ↓
Is CRS geographic?
   │
   ├── Yes
   │     ↓
   │   Estimate suitable UTM CRS
   │     ↓
   │   Transform geometry
   │     ↓
   │   Calculate measurement
   │
   └── No
         ↓
      Use existing projected CRS
         ↓
      Calculate measurement
```

The application uses GeoPandas' `estimate_utm_crs()` to select an appropriate UTM projection based on the geographic location of the input data.

This allows measurements to be calculated in meters and square meters rather than degrees.

---

# 8. Database Design

SQLite is used as the database because the assignment is a lightweight backend application and does not require a spatial database for the current implementation.

## Files Table

Stores information about uploaded files:

```text
files
├── id
├── filename
├── file_path
├── file_type
├── status
├── feature_count
└── crs
```

## Measurements Table

Stores calculated measurements:

```text
measurements
├── id
├── file_id
├── feature_index
├── geometry_type
├── measurement_type
├── value
└── unit
```

A spatial database such as PostgreSQL with PostGIS could be considered for a larger production system.

---

# 9. Design Decisions

## FastAPI

FastAPI was selected because it provides:

- Simple REST API development
- Automatic OpenAPI documentation
- Swagger UI
- Type hints
- File upload support
- Good performance for API applications

Django REST Framework was considered as an alternative, but FastAPI was chosen because the assignment focuses on a relatively small backend API.

---

## GeoPandas

GeoPandas was selected because it provides convenient support for reading and processing geospatial files.

It also integrates well with:

- Shapely
- PyProj
- Coordinate transformations

---

## Shapely

Shapely is used for geometry-specific operations such as:

- Polygon area
- LineString length
- Geometry type identification

---

## UTM Projection

Instead of manually selecting a fixed projected CRS, the application uses `estimate_utm_crs()`.

This provides a more general approach because the appropriate UTM zone depends on the geographic location of the input data.

---

## SQLite

SQLite was selected because:

- The assignment does not require a spatial database.
- The application is intended to run locally.
- It keeps the setup simple.
- SQLAlchemy allows the database layer to be changed later if required.

For a larger production geospatial system, PostgreSQL with PostGIS would be a stronger alternative.

---

## SQLAlchemy

SQLAlchemy provides an ORM layer between the FastAPI application and the database.

It also makes it easier to migrate to another relational database in the future.

---

# 10. Testing

The project includes two representative Pytest tests.

## Test 1 — Successful KML Processing

Tests that a valid KML file:

- Is uploaded successfully
- Contains the expected number of features
- Has the expected CRS
- Completes processing successfully

## Test 2 — Empty KML Validation

Tests that an empty KML file:

- Is rejected
- Returns HTTP 400
- Returns the expected validation message

Run the tests using:

```bash
uv run pytest
```

Expected result:

```text
2 passed
```

---

# 11. Current Scope

The current implementation focuses on **KML processing**.

Supported geometry types include:

- Point
- LineString
- Polygon

Measurements currently supported:

- Polygon → Area
- LineString → Length
- Point → No measurement

Shapefile and ZIP-based Shapefile processing are not currently implemented.

---

# 12. Learning

Through this project, I worked with:

- FastAPI REST API development
- File upload handling
- GeoPandas for geospatial data processing
- Shapely geometry operations
- CRS and coordinate transformations
- UTM projection selection
- SQLAlchemy ORM
- SQLite database integration
- API validation and error handling
- Pytest API testing
- Structuring a backend application into routes, services, and database layers

The project also helped me understand why geospatial measurements cannot simply be calculated directly from latitude/longitude coordinates.

---

# 13. Future Scope

The following improvements could be added in future versions:

- Support for Shapefile uploads
- Support for ZIP archives containing Shapefile datasets
- Store complete feature geometry and properties in the database
- Add Pydantic response schemas
- Add stronger database relationships and transaction handling
- Add authentication and authorization
- Support asynchronous/background processing for large files
- Add file size limits and stronger upload security
- Use PostgreSQL with PostGIS for production-scale geospatial data
- Add more comprehensive automated tests
- Add Docker-based deployment
- Add cloud deployment and object storage for uploaded files
- Support additional geospatial formats such as GeoJSON

---

# 14. Submission

This project is developed as part of the Aereo Software Development Engineer Intern assignment.

## GitHub Repository

```text
<YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
```
