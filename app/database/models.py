from sqlalchemy import Column, Float, Integer, String

from app.database.database import Base


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="uploaded")
    feature_count = Column(Integer, nullable=True)
    crs = Column(String, nullable=True)


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=False)
    feature_index = Column(Integer, nullable=False)
    geometry_type = Column(String, nullable=False)
    measurement_type = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)