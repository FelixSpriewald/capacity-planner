"""
CRUD Operations für Sprints
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.sprints import Sprint
from app.db.models import SprintStatus
from app.schemas.schemas import SprintCreate, SprintUpdate


def get_sprints(db: Session, skip: int = 0, limit: int = 100) -> List[Sprint]:
    """Alle Sprints abrufen"""
    return db.query(Sprint).offset(skip).limit(limit).all()


def get_sprint(db: Session, sprint_id: int) -> Optional[Sprint]:
    """Ein Sprint by ID"""
    return db.query(Sprint).filter(Sprint.sprint_id == sprint_id).first()


def create_sprint(db: Session, sprint: SprintCreate) -> Sprint:
    """Neuen Sprint erstellen (immer DRAFT)"""
    db_sprint = Sprint(
        **sprint.model_dump(),
        status=SprintStatus.DRAFT
    )
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint


def update_sprint(db: Session, sprint_id: int, sprint_update: SprintUpdate) -> Optional[Sprint]:
    """Sprint aktualisieren"""
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return None

    update_data = sprint_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_sprint, field):
            setattr(db_sprint, field, value)

    db.commit()
    db.refresh(db_sprint)
    return db_sprint


def delete_sprint(db: Session, sprint_id: int) -> bool:
    """Sprint löschen"""
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return False

    db.delete(db_sprint)
    db.commit()
    return True
