"""
Sprints API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.crud.sprints import get_sprints, get_sprint, create_sprint, update_sprint, delete_sprint
from app.schemas.schemas import SprintResponse, SprintCreate, SprintUpdate

router = APIRouter()

SPRINT_NOT_FOUND = "Sprint not found"


@router.get("/", response_model=List[SprintResponse])
def list_sprints(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Alle Sprints abrufen"""
    sprints = get_sprints(db, skip=skip, limit=limit)
    return sprints


@router.get("/{sprint_id}", response_model=SprintResponse)
def get_sprint_by_id(sprint_id: int, db: Session = Depends(get_db)):
    """Ein Sprint by ID abrufen"""
    sprint = get_sprint(db, sprint_id=sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)
    return sprint


@router.post("/", response_model=SprintResponse)
def create_new_sprint(sprint: SprintCreate, db: Session = Depends(get_db)):
    """Neuen Sprint erstellen (Status: DRAFT)"""
    if sprint.end_date < sprint.start_date:
        raise HTTPException(status_code=422, detail="End date must be >= start date")

    try:
        return create_sprint(db, sprint=sprint)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{sprint_id}", response_model=SprintResponse)
def update_sprint_by_id(sprint_id: int, sprint_update: SprintUpdate, db: Session = Depends(get_db)):
    """Sprint aktualisieren (inkl. Status-Wechsel)"""
    # Validierung für Date-Updates
    if sprint_update.start_date and sprint_update.end_date:
        if sprint_update.end_date < sprint_update.start_date:
            raise HTTPException(status_code=422, detail="End date must be >= start date")

    sprint = update_sprint(db, sprint_id=sprint_id, sprint_update=sprint_update)
    if not sprint:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)
    return sprint


@router.delete("/{sprint_id}")
def delete_sprint_by_id(sprint_id: int, db: Session = Depends(get_db)):
    """Sprint löschen"""
    success = delete_sprint(db, sprint_id=sprint_id)
    if not success:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)
    return {"message": "Sprint deleted successfully"}
