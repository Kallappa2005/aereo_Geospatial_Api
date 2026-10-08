from fastapi import FastAPI
from app.routes.files import router as files_router

from app.database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aereo Geospatial File Measurement API",
    description="Backend API for processing KML files and calculating geospatial measurements.",
    version="1.0.0",
)

app.include_router(files_router)

@app.get("/")
def root():
    return {"message": "Aereo Geospatial API is running"}