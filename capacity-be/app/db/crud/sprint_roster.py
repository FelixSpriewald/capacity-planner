"""
CRUD Operations für Sprint Roster
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.db.models.sprint_roster import SprintRoster
from app.db.models.members import Member
from app.schemas.schemas import SprintRosterCreate, SprintRosterUpdate


def get_sprint_roster(db: Session, sprint_id: int) -> List[SprintRoster]:
    """Roster für einen Sprint abrufen"""
    return db.query(SprintRoster).options(
        joinedload(SprintRoster.member)
    ).filter(SprintRoster.sprint_id == sprint_id).all()


def get_roster_entry(db: Session, sprint_id: int, member_id: int) -> Optional[SprintRoster]:
    """Einzelnen Roster-Eintrag abrufen"""
    return db.query(SprintRoster).filter(
        SprintRoster.sprint_id == sprint_id,
        SprintRoster.member_id == member_id
    ).first()


def add_member_to_sprint(db: Session, sprint_id: int, roster_data: SprintRosterCreate) -> SprintRoster:
    """Member zu Sprint hinzufügen"""
    # Prüfen ob bereits im Roster
    existing = get_roster_entry(db, sprint_id, roster_data.member_id)
    if existing:
        raise ValueError(f"Member {roster_data.member_id} is already in sprint {sprint_id}")

    db_roster = SprintRoster(
        sprint_id=sprint_id,
        **roster_data.model_dump()
    )
    db.add(db_roster)
    db.commit()
    db.refresh(db_roster)
    return db_roster


def update_roster_entry(db: Session, sprint_id: int, member_id: int, roster_update: SprintRosterUpdate) -> Optional[SprintRoster]:
    """Roster-Eintrag aktualisieren"""
    db_roster = get_roster_entry(db, sprint_id, member_id)
    if not db_roster:
        return None

    update_data = roster_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_roster, field):
            setattr(db_roster, field, value)

    db.commit()
    db.refresh(db_roster)
    return db_roster


def remove_member_from_sprint(db: Session, sprint_id: int, member_id: int) -> bool:
    """Member aus Sprint entfernen"""
    db_roster = get_roster_entry(db, sprint_id, member_id)
    if not db_roster:
        return False

    db.delete(db_roster)
    db.commit()
    return True
