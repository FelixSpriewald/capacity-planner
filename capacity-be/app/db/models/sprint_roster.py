from sqlalchemy import Column, Integer, ForeignKey, Date, Index
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class SprintRoster(Base):
    """Sprint Roster Model - Mapping von Members zu Sprints"""
    __tablename__ = "sprint_roster"

    # Composite Primary Key
    sprint_id = Column(Integer, ForeignKey("sprints.sprint_id"), primary_key=True)
    member_id = Column(Integer, ForeignKey("members.member_id"), primary_key=True)

    allocation = Column(Numeric(3, 2), nullable=False, default=1.0)  # 0.00 - 1.00
    assignment_from = Column(Date, nullable=True)  # Optional: Einschränkung des verfügbaren Zeitraums
    assignment_to = Column(Date, nullable=True)    # Optional: Einschränkung des verfügbaren Zeitraums

    # Relationships
    sprint = relationship("Sprint", back_populates="sprint_rosters")
    member = relationship("Member", back_populates="sprint_rosters")

    # Index für bessere Performance
    __table_args__ = (
        Index("idx_sprint_roster_sprint_member", "sprint_id", "member_id"),
    )

    def __repr__(self):
        return f"<SprintRoster(sprint_id={self.sprint_id}, member_id={self.member_id}, allocation={self.allocation})>"
