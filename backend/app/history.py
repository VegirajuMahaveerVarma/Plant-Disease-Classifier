from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Scan

def list_scans(db: Session, limit: int = 50) -> list[Scan]:
    return list(db.scalars(select(Scan).order_by(Scan.created_at.desc()).limit(limit)))

def delete_scan(db: Session, scan_id: int) -> bool:
    scan = db.get(Scan, scan_id)
    if scan is None:
        return False
    db.delete(scan)
    db.commit()
    return True
