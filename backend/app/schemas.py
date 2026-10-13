from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class PredictionItem(BaseModel):
    class_name: str
    confidence: float = Field(ge=0, le=1)

class PredictionResponse(BaseModel):
    scan_id: int
    filename: str
    predicted_class: str
    confidence: float = Field(ge=0, le=1)
    top_predictions: list[PredictionItem]
    model_version: str
    note: str

class ScanRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    predicted_class: str
    confidence: float
    status: str
    model_version: str
    created_at: datetime
    note: str | None = None
