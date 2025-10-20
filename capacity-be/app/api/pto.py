"""
PTO (Personal Time Off) API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.crud import pto as pto_crud
from app.db.crud import members as member_crud
from app.schemas.schemas import PTO, PTOCreate, PTOUpdate
from app.services.validation import ValidationService, ValidationError

router = APIRouter()

# Error Messages
MEMBER_NOT_FOUND = "Member nicht gefunden"
PTO_NOT_FOUND = "PTO-Eintrag nicht gefunden"
VALIDATION_ERROR = "Validierungsfehler"


@router.get("/", response_model=List[PTO])
def get_pto_list(
    member_id: Optional[int] = None,
    sprint_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Alle PTO-Einträge abrufen mit optionalen Filtern"""
    return pto_crud.get_pto_list(db, member_id=member_id, sprint_id=sprint_id, skip=skip, limit=limit)


@router.get("/{pto_id}", response_model=PTO)
def get_pto(pto_id: int, db: Session = Depends(get_db)):
    """Ein PTO-Eintrag by ID"""
    db_pto = pto_crud.get_pto(db, pto_id=pto_id)
    if db_pto is None:
        raise HTTPException(status_code=404, detail=PTO_NOT_FOUND)
    return db_pto


@router.post("/", response_model=PTO, status_code=201)
def create_pto(pto: PTOCreate, db: Session = Depends(get_db)):
    """Neuen PTO-Eintrag erstellen"""
    try:
        # Member existiert?
        member = member_crud.get_member(db, pto.member_id)
        if not member:
            raise HTTPException(status_code=404, detail=MEMBER_NOT_FOUND)

        # Validation Service initialisieren
        validation_service = ValidationService(db)

        # PTO-Validierung
        validation_service.validate_pto_dates(pto.member_id, pto.from_date, pto.to_date)

        return pto_crud.create_pto(db=db, pto=pto)

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"{VALIDATION_ERROR}: {str(e)}")


@router.put("/{pto_id}", response_model=PTO)
def update_pto(pto_id: int, pto_update: PTOUpdate, db: Session = Depends(get_db)):
    """PTO-Eintrag aktualisieren"""
    try:
        # PTO existiert?
        existing_pto = pto_crud.get_pto(db, pto_id)
        if not existing_pto:
            raise HTTPException(status_code=404, detail=PTO_NOT_FOUND)

        update_data = pto_update.model_dump(exclude_unset=True)

        # Validation Service initialisieren
        validation_service = ValidationService(db)

        # Validiere Datumsangaben falls geändert
        from_date = update_data.get('from_date', existing_pto.from_date)
        to_date = update_data.get('to_date', existing_pto.to_date)
        member_id = existing_pto.member_id

        validation_service.validate_pto_dates(member_id, from_date, to_date, exclude_pto_id=pto_id)

        result = pto_crud.update_pto(db=db, pto_id=pto_id, pto_update=update_data)
        if result is None:
            raise HTTPException(status_code=404, detail=PTO_NOT_FOUND)
        return result

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"{VALIDATION_ERROR}: {str(e)}")


@router.delete("/{pto_id}")
def delete_pto(pto_id: int, db: Session = Depends(get_db)):
    """PTO-Eintrag löschen"""
    success = pto_crud.delete_pto(db=db, pto_id=pto_id)
    if not success:
        raise HTTPException(status_code=404, detail=PTO_NOT_FOUND)
    return {"message": "PTO-Eintrag erfolgreich gelöscht"}
