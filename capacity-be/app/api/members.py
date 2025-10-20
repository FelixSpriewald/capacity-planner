"""
Members API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.crud.members import get_members, get_all_members, get_member, create_member, update_member, delete_member
from app.schemas.schemas import MemberResponse, MemberCreate
from app.services.validation import ValidationService, ValidationError

router = APIRouter()

MEMBER_NOT_FOUND = "Member not found"


@router.get("/", response_model=List[MemberResponse])
def list_members(skip: int = 0, limit: int = 100, include_inactive: bool = False, db: Session = Depends(get_db)):
    """Alle Members abrufen (optional auch inaktive)"""
    if include_inactive:
        members = get_all_members(db, skip=skip, limit=limit)
    else:
        members = get_members(db, skip=skip, limit=limit)
    return members


@router.get("/{member_id}", response_model=MemberResponse)
def get_member_by_id(member_id: int, db: Session = Depends(get_db)):
    """Ein Member by ID abrufen"""
    member = get_member(db, member_id=member_id)
    if not member:
        raise HTTPException(status_code=404, detail=MEMBER_NOT_FOUND)
    return member


@router.post("/", response_model=MemberResponse)
def create_new_member(member: MemberCreate, db: Session = Depends(get_db)):
    """Neuen Member erstellen"""
    validator = ValidationService(db)

    try:
        # Erweiterte Validierung
        validator.validate_employment_ratio(float(member.employment_ratio))

        return create_member(db, member=member)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{member_id}", response_model=MemberResponse)
def update_member_by_id(member_id: int, member_update: MemberCreate, db: Session = Depends(get_db)):
    """Member aktualisieren"""
    validator = ValidationService(db)

    try:
        # Erweiterte Validierung
        validator.validate_employment_ratio(float(member_update.employment_ratio))

        member = update_member(db, member_id=member_id, member_update=member_update.model_dump())
        if not member:
            raise HTTPException(status_code=404, detail=MEMBER_NOT_FOUND)
        return member

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{member_id}")
def delete_member_by_id(member_id: int, db: Session = Depends(get_db)):
    """Member deaktivieren"""
    success = delete_member(db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail=MEMBER_NOT_FOUND)
    return {"message": "Member deactivated successfully"}
