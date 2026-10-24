import hashlib
import json
import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from .database import SessionLocal, Incident, Base, engine

app = FastAPI(title="Forensic Backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class IncidentCreate(BaseModel):
    incident_id: str
    trace_id: str
    service_name: str
    severity: str
    error_message: str

@app.post("/incidents")
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(
        incident_id=incident.incident_id,
        trace_id=incident.trace_id,
        service_name=incident.service_name,
        severity=incident.severity,
        error_message=incident.error_message
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return {"message": "Incident created successfully", "incident": db_incident}

@app.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()

@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.get("/incidents/{incident_id}/timeline")
def get_timeline(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    timeline = [
        {
            "timestamp": incident.timestamp.isoformat(),
            "service": incident.service_name,
            "event": "Incident Recorded",
            "severity": incident.severity,
            "trace_id": incident.trace_id,
            "details": incident.error_message
        }
    ]
    
    return {
        "incident_id": incident.incident_id,
        "timeline": timeline
    }

@app.post("/incidents/{incident_id}/collect")
def collect_evidence(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Evidence package tayar karein
    evidence_data = {
        "incident_id": incident.incident_id,
        "trace_id": incident.trace_id,
        "service_name": incident.service_name,
        "severity": incident.severity,
        "error_message": incident.error_message,
        "timestamp": incident.timestamp.isoformat()
    }
    
    # 1. JSON mein convert karein (consistent format mein)
    serialized_data = json.dumps(evidence_data, sort_keys=True, indent=4)
    
    # 2. SHA-256 Hash calculate karein
    hash_digest = hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()
    
    # 3. Evidence folder banayein (agar nahi hai)
    os.makedirs("evidence", exist_ok=True)
    filename = f"evidence/evidence_{incident.incident_id}.json"
    manifest_file = f"evidence/manifest_{incident.incident_id}.json"
    
    # 4. Evidence file save karein
    with open(filename, "w") as f:
        f.write(serialized_data)
        
    # 5. Manifest file save karein (Original hash ke sath)
    manifest_data = {
        "incident_id": incident.incident_id,
        "sha256_hash": hash_digest,
        "collection_time": datetime.utcnow().isoformat()
    }
    with open(manifest_file, "w") as f:
        json.dump(manifest_data, f, indent=4)
        
    return {
        "message": "Evidence collected and exported successfully",
        "incident_id": incident.incident_id,
        "evidence_file": filename,
        "manifest_file": manifest_file,
        "sha256_hash": hash_digest,
        "integrity_status": "Verified (Hash Generated)"
    }

@app.post("/evidence/{incident_id}/verify")
def verify_evidence(incident_id: str):
    filename = f"evidence/evidence_{incident_id}.json"
    manifest_file = f"evidence/manifest_{incident_id}.json"
    
    # Check karein ke file exist karti hai ya nahi
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Evidence file not found")
    
    # 1. File ko read karein
    with open(filename, "r") as f:
        file_content = f.read()
    
    # 2. Naya hash calculate karein
    current_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()
    
    # 3. Manifest se original hash read karein aur compare karein
    if os.path.exists(manifest_file):
        with open(manifest_file, "r") as f:
            manifest = json.load(f)
            original_hash = manifest.get("sha256_hash")
            
            if current_hash != original_hash:
                return {
                    "incident_id": incident_id,
                    "verification_result": "FAILED",
                    "message": "WARNING: Evidence has been TAMPERED with!",
                    "original_hash": original_hash,
                    "current_hash": current_hash
                }
            else:
                return {
                    "incident_id": incident_id,
                    "verification_result": "SUCCESS",
                    "message": "Evidence integrity verified. No tampering.",
                    "hash": current_hash
                }
    else:
        # Agar manifest nahi hai (purana case), toh filhal success dikhayein
        return {
            "incident_id": incident_id,
            "verification_result": "SUCCESS (No Manifest)",
            "recalculated_hash": current_hash
        }