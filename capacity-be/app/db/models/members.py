from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class Member(Base):
    """Team Member Model"""
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    employment_ratio = Column(Numeric(3, 2), nullable=False, default=1.0)  # 0.00 - 1.00
    region_code = Column(String(10), nullable=True)  # e.g., "DE-NW", "UA"
    active = Column(Boolean, nullable=False, default=True)

    # Relationships
    sprint_rosters = relationship("SprintRoster", back_populates="member")
    ptos = relationship("PTO", back_populates="member")
    availability_overrides = relationship("AvailabilityOverride", back_populates="member")

    def __repr__(self):
        return f"<Member(id={self.member_id}, name='{self.name}', region='{self.region_code}')>"
