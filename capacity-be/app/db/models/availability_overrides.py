from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class AvailabilityState(enum.Enum):
    """Availability State Enum"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    HALF = "half"


class AvailabilityOverride(Base):
    """Availability Override Model - Überschreibt automatisch berechnete Verfügbarkeit"""
    __tablename__ = "availability_overrides"

    # Composite Primary Key
    sprint_id = Column(Integer, ForeignKey("sprints.sprint_id"), primary_key=True)
    member_id = Column(Integer, ForeignKey("members.member_id"), primary_key=True)
    day = Column(Date, primary_key=True)

    state = Column(Enum(AvailabilityState), nullable=False)
    reason = Column(Text, nullable=True)

    # Relationships
    sprint = relationship("Sprint", back_populates="availability_overrides")
    member = relationship("Member", back_populates="availability_overrides")

    # Unique constraint für Sprint/Member/Day Kombination
    __table_args__ = (
        Index("idx_availability_sprint_member_day", "sprint_id", "member_id", "day", unique=True),
    )

    def __repr__(self):
        return f"<AvailabilityOverride(sprint_id={self.sprint_id}, member_id={self.member_id}, day={self.day}, state='{self.state.value}')>"
