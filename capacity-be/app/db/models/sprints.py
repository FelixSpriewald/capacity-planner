from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class SprintStatus(enum.Enum):
    """Sprint Status Enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class Sprint(Base):
    """Sprint Model"""
    __tablename__ = "sprints"

    sprint_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(SprintStatus), nullable=False, default=SprintStatus.DRAFT)

    # Relationships
    sprint_rosters = relationship("SprintRoster", back_populates="sprint")
    availability_overrides = relationship("AvailabilityOverride", back_populates="sprint")

    def __repr__(self):
        return f"<Sprint(id={self.sprint_id}, name='{self.name}', status='{self.status.value}')>"
