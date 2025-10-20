from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import date, datetime

from app.db.base import Base


class SprintStatus(enum.Enum):
    """Sprint Status Enum"""
    PLANNED = "planned"
    ACTIVE = "active"
    FINISHED = "finished"


class Sprint(Base):
    """Sprint Model"""
    __tablename__ = "sprints"

    sprint_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(SprintStatus), nullable=False, default=SprintStatus.PLANNED)

    # Relationships
    sprint_rosters = relationship("SprintRoster", back_populates="sprint")
    availability_overrides = relationship("AvailabilityOverride", back_populates="sprint")

    def calculate_status_from_dates(self) -> SprintStatus:
        """Calculate status based on current date and sprint dates"""
        today = date.today()

        if today < self.start_date:
            return SprintStatus.PLANNED
        elif self.start_date <= today <= self.end_date:
            return SprintStatus.ACTIVE
        else:
            return SprintStatus.FINISHED

    def update_status_automatically(self):
        """Update status based on current date"""
        self.status = self.calculate_status_from_dates()

    def __repr__(self):
        return f"<Sprint(id={self.sprint_id}, name='{self.name}', status='{self.status.value}')>"
