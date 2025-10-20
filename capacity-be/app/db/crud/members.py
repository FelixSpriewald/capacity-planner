"""
CRUD Operations für Members
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.members import Member
from app.schemas.schemas import MemberCreate


def get_members(db: Session, skip: int = 0, limit: int = 100) -> List[Member]:
    """Alle Members abrufen"""
    return db.query(Member).filter(Member.active == True).offset(skip).limit(limit).all()


def get_member(db: Session, member_id: int) -> Optional[Member]:
    """Ein Member by ID"""
    return db.query(Member).filter(Member.member_id == member_id, Member.active == True).first()


def create_member(db: Session, member: MemberCreate) -> Member:
    """Neuen Member erstellen"""
    db_member = Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_member(db: Session, member_id: int, member_update: dict) -> Optional[Member]:
    """Member aktualisieren"""
    db_member = get_member(db, member_id)
    if not db_member:
        return None

    for field, value in member_update.items():
        if hasattr(db_member, field):
            setattr(db_member, field, value)

    db.commit()
    db.refresh(db_member)
    return db_member


def delete_member(db: Session, member_id: int) -> bool:
    """Member deaktivieren (soft delete)"""
    db_member = get_member(db, member_id)
    if not db_member:
        return False

    db_member.active = False
    db.commit()
    return True
