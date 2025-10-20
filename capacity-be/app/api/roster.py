"""
Sprint Roster API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.crud.sprint_roster import (
    get_sprint_roster, add_member_to_sprint,
    update_roster_entry, remove_member_from_sprint
)
from app.schemas.schemas import (
    SprintRosterResponse, SprintRosterCreate, SprintRosterUpdate
)
from app.services.validation import ValidationService, ValidationError

router = APIRouter()

ROSTER_NOT_FOUND = "Roster entry not found"


@router.get("/{sprint_id}/roster", response_model=List[SprintRosterResponse])
def get_roster_for_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """Roster für einen Sprint abrufen"""
    roster = get_sprint_roster(db, sprint_id=sprint_id)

    # Member-Namen hinzufügen
    result = []
    for entry in roster:
        data = SprintRosterResponse.model_validate(entry)
        data.member_name = entry.member.name if entry.member else None
        result.append(data)

    return result


@router.post("/{sprint_id}/roster", response_model=SprintRosterResponse)
def add_member_to_roster(
    sprint_id: int, 
    roster_data: SprintRosterCreate, 
    db: Session = Depends(get_db)
):
    """Member zu Sprint hinzufügen"""
    validator = ValidationService(db)
    
    try:
        # Validierungen
        validator.validate_roster_uniqueness(sprint_id, roster_data.member_id)
        validator.validate_assignment_window(sprint_id, roster_data.assignment_from, roster_data.assignment_to)
        validator.validate_allocation_range(float(roster_data.allocation))
        
        entry = add_member_to_sprint(db, sprint_id=sprint_id, roster_data=roster_data)
        result = SprintRosterResponse.model_validate(entry)
        result.member_name = entry.member.name if entry.member else None
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.put("/{sprint_id}/roster/{member_id}", response_model=SprintRosterResponse)
def update_roster_member(
    sprint_id: int,
    member_id: int,
    roster_update: SprintRosterUpdate,
    db: Session = Depends(get_db)
):
    """Roster-Eintrag aktualisieren"""
    validator = ValidationService(db)
    
    try:
        # Validierungen
        validator.validate_assignment_window(sprint_id, roster_update.assignment_from, roster_update.assignment_to)
        validator.validate_allocation_range(float(roster_update.allocation))
        
        entry = update_roster_entry(db, sprint_id=sprint_id, member_id=member_id, roster_update=roster_update)
        if not entry:
            raise HTTPException(status_code=404, detail=ROSTER_NOT_FOUND)
        
        result = SprintRosterResponse.model_validate(entry)
        result.member_name = entry.member.name if entry.member else None
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/{sprint_id}/roster/{member_id}")
def remove_member_from_roster(sprint_id: int, member_id: int, db: Session = Depends(get_db)):
    """Member aus Sprint entfernen"""
    success = remove_member_from_sprint(db, sprint_id=sprint_id, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail=ROSTER_NOT_FOUND)

    return {"message": "Member removed from sprint successfully"}
