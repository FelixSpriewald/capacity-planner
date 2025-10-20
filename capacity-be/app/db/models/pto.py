from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class PTO(Base):
    """Personal Time Off Model"""
    __tablename__ = "pto"

    pto_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id"), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    type = Column(String(50), nullable=False, default="vacation")  # vacation, sick, personal, etc.
    notes = Column(Text, nullable=True)

    # Relationships
    member = relationship("Member", back_populates="ptos")

    def __repr__(self):
        return f"<PTO(id={self.pto_id}, member_id={self.member_id}, from={self.from_date}, to={self.to_date}, type='{self.type}')>"
