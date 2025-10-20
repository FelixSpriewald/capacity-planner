"""
CRUD Operations für PTO (Personal Time Off)
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.db.models.pto import PTO
from app.db.models.members import Member
from app.schemas.schemas import PTOCreate


def get_pto_list(db: Session, member_id: Optional[int] = None, sprint_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[PTO]:
    """PTO-Einträge abrufen mit optionalen Filtern"""
    query = db.query(PTO).options(joinedload(PTO.member))

    if member_id:
        query = query.filter(PTO.member_id == member_id)

    if sprint_id:
        # Filter PTO die einen Sprint überlappen - dafür Sprint-Daten holen
        from app.db.crud.sprints import get_sprint
        sprint = get_sprint(db, sprint_id)
        if sprint:
            query = query.filter(
                PTO.from_date <= sprint.end_date,
                PTO.to_date >= sprint.start_date
            )

    return query.offset(skip).limit(limit).all()


def get_pto(db: Session, pto_id: int) -> Optional[PTO]:
    """Ein PTO-Eintrag by ID"""
    return db.query(PTO).options(joinedload(PTO.member)).filter(PTO.pto_id == pto_id).first()


def create_pto(db: Session, pto: PTOCreate) -> PTO:
    """Neuen PTO-Eintrag erstellen"""
    db_pto = PTO(**pto.model_dump())
    db.add(db_pto)
    db.commit()
    db.refresh(db_pto)
    return db_pto


def update_pto(db: Session, pto_id: int, pto_update: dict) -> Optional[PTO]:
    """PTO-Eintrag aktualisieren"""
    db_pto = get_pto(db, pto_id)
    if not db_pto:
        return None

    for field, value in pto_update.items():
        if hasattr(db_pto, field):
            setattr(db_pto, field, value)

    db.commit()
    db.refresh(db_pto)
    return db_pto


def delete_pto(db: Session, pto_id: int) -> bool:
    """PTO-Eintrag löschen"""
    db_pto = get_pto(db, pto_id)
    if not db_pto:
        return False

    db.delete(db_pto)
    db.commit()
    return True
