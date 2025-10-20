from sqlalchemy import Column, Integer, String, Date, Boolean

from app.db.base import Base


class Holiday(Base):
    """Holiday Model"""
    __tablename__ = "holidays"

    holiday_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    region_code = Column(String(10), nullable=False)  # e.g., "DE-NW", "UA"
    name = Column(String(255), nullable=False)
    is_company_day = Column(Boolean, nullable=False, default=True)  # Company-weiter Feiertag oder nur regional

    def __repr__(self):
        return f"<Holiday(id={self.holiday_id}, date={self.date}, region='{self.region_code}', name='{self.name}')>"
