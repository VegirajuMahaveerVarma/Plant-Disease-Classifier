from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
import logging
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from sqlalchemy import text
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .history import delete_scan, list_scans
from .models import Scan
from .predictor import PlantPredictor
from .schemas import PredictionResponse, ScanRecord

logger = logging.getLogger(__name__)
settings = get_settings()
predictor = PlantPredictor()
DISEASES = [
 {"slug":"tomato-early-blight","plant":"Tomato","name":"Early blight","category":"Disease","symptoms":"Brown lesions with concentric rings, often with yellowing around affected areas.","guidance":"Avoid prolonged leaf wetness, remove affected plant debris, and consult local agricultural extension guidance."},
 {"slug":"tomato-late-blight","plant":"Tomato","name":"Late blight","category":"Disease","symptoms":"Water-soaked or dark lesions that may expand quickly in humid conditions.","guidance":"Inspect plants regularly, avoid overhead watering where practical, and seek local expert advice if spread is rapid."},
 {"slug":"tomato-healthy","plant":"Tomato","name":"Healthy","category":"Healthy","symptoms":"No obvious symptoms are described by this reference entry.","guidance":"Continue regular monitoring and maintain good crop hygiene."},
 {"slug":"potato-early-blight","plant":"Potato","name":"Early blight","category":"Disease","symptoms":"Dark leaf spots may develop concentric rings and surrounding yellow tissue.","guidance":"Rotate crops where appropriate, manage crop residue, and consult local agricultural extension guidance."},
 {"slug":"pepper-bacterial-spot","plant":"Pepper","name":"Bacterial spot","category":"Disease","symptoms":"Small water-soaked spots may darken; symptoms vary with conditions.","guidance":"Use clean seed and transplants when possible and ask a local expert about confirmed cases."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if not predictor.load():
        logger.warning("No valid trained model loaded; predictions remain disabled.")
    yield

app = FastAPI(title="AgriVision AI API", version="0.1.0", description="Plant image classification API. Predictions require a trained checkpoint.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=False, allow_methods=["GET","POST","DELETE"], allow_headers=["Content-Type"])

@app.get("/")
def root():
    return {"name":"AgriVision AI API","docs":"/docs","health":"/health"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    ready = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        ready = False
    return {"status":"ok" if ready else "degraded","database":"connected" if ready else "unavailable","model":"ready" if predictor.ready else "not_configured","prediction_available":predictor.ready}

@app.get("/api/v1/diseases")
def diseases():
    return {"items": DISEASES}

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not predictor.ready:
        raise HTTPException(status_code=503, detail="Model is not configured yet. See README.md to train and configure it.")
    filename = Path(file.filename or "plant-image").name[:255]
    if file.content_type not in {"image/jpeg","image/png","image/webp"}:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, or WebP image.")
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Image exceeds {settings.max_upload_mb} MB upload limit.")
    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image = Image.open(BytesIO(content)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid image.") from None
    predictions = predictor.predict(image)
    best = predictions[0]
    record = Scan(filename=filename, predicted_class=best["class_name"], confidence=best["confidence"], status="prediction", model_version="resnet18-local-v1", note="AI prediction only; verify with a qualified agricultural professional before acting.")
    db.add(record)
    db.commit()
    db.refresh(record)
    return PredictionResponse(scan_id=record.id, filename=filename, predicted_class=best["class_name"], confidence=best["confidence"], top_predictions=predictions, model_version=record.model_version, note=record.note or "")

@app.get("/api/v1/scans", response_model=list[ScanRecord])
def scans(limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    return list_scans(db, limit)

@app.delete("/api/v1/scans/{scan_id}", status_code=204)
def remove_scan(scan_id: int, db: Session = Depends(get_db)):
    if not delete_scan(db, scan_id):
        raise HTTPException(status_code=404, detail="Scan not found.")
    return None
