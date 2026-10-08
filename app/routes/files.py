from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import FileRecord, Measurement
from app.services.kml_processor import process_kml


router = APIRouter(prefix="/api/files", tags=["Files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".kml"):
        raise HTTPException(
            status_code=400,
            detail="Only KML files are supported.",
        )

    file_path = UPLOAD_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    file_record = FileRecord(
        filename=file.filename,
        file_path=str(file_path),
        file_type="kml",
        status="uploaded",
    )

    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    try:
        features = process_kml(str(file_path))

        for feature in features:
            measurement = feature["measurement"]

            if measurement is None:
                continue

            db.add(
                Measurement(
                    file_id=file_record.id,
                    feature_index=feature["feature_index"],
                    geometry_type=feature["geometry_type"],
                    measurement_type=measurement["measurement_type"],
                    value=measurement["value"],
                    unit=measurement["unit"],
                )
            )

        file_record.feature_count = len(features)

        file_record.crs = (
            features[0]["crs"]
            if features and features[0]["crs"]
            else None
        )

        file_record.status = "COMPLETED"

        db.commit()

    except ValueError as exc:
        file_record.status = "FAILED"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        file_record.status = "FAILED"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Failed to process KML file.",
        )

    return {
        "id": file_record.id,
        "filename": file_record.filename,
        "file_type": file_record.file_type,
        "feature_count": file_record.feature_count,
        "crs": file_record.crs,
        "status": file_record.status,
    }


@router.get("/{file_id}/")
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id)
        .first()
    )

    if file_record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    return {
        "id": file_record.id,
        "filename": file_record.filename,
        "feature_count": file_record.feature_count,
        "crs": file_record.crs,
        "status": file_record.status,
    }


@router.get("/{file_id}/measurements/")
def get_measurements(
    file_id: int,
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id)
        .first()
    )

    if file_record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    measurements = (
        db.query(Measurement)
        .filter(Measurement.file_id == file_id)
        .all()
    )

    return {
        "file_id": file_id,
        "filename": file_record.filename,
        "measurements": [
            {
                "feature_index": measurement.feature_index,
                "geometry_type": measurement.geometry_type,
                "measurement_type": measurement.measurement_type,
                "value": measurement.value,
                "unit": measurement.unit,
            }
            for measurement in measurements
        ],
    }