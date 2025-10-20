"""
Sprints API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.crud.sprints import get_sprints, get_sprint, create_sprint, update_sprint, delete_sprint
from app.schemas.schemas import SprintResponse, SprintCreate, SprintUpdate
from app.services.validation import ValidationService, ValidationError

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
    validator = ValidationService(db)

    try:
        # Erweiterte Validierung
        validator.validate_sprint_dates(sprint.start_date, sprint.end_date)

        return create_sprint(db, sprint=sprint)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.patch("/{sprint_id}", response_model=SprintResponse)
def update_sprint_by_id(sprint_id: int, sprint_update: SprintUpdate, db: Session = Depends(get_db)):
    """Sprint aktualisieren (inkl. Status-Wechsel)"""
    validator = ValidationService(db)

    try:
        # Validierung für Date-Updates
        if sprint_update.start_date or sprint_update.end_date:
            # Hole aktuelle Werte falls nur eine Seite geändert wird
            current_sprint = get_sprint(db, sprint_id)
            if not current_sprint:
                raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)

            start_date = sprint_update.start_date or current_sprint.start_date
            end_date = sprint_update.end_date or current_sprint.end_date

            validator.validate_sprint_dates(start_date, end_date)

        sprint = update_sprint(db, sprint_id=sprint_id, sprint_update=sprint_update)
        if not sprint:
            raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)
        return sprint

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/{sprint_id}")
def delete_sprint_by_id(sprint_id: int, db: Session = Depends(get_db)):
    """Sprint löschen"""
    success = delete_sprint(db, sprint_id=sprint_id)
    if not success:
        raise HTTPException(status_code=404, detail=SPRINT_NOT_FOUND)
    return {"message": "Sprint deleted successfully"}
