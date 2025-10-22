from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.db.models import SprintStatus, AvailabilityState


# === Base Schemas ===

class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    employment_ratio: Decimal = Field(..., ge=0.0, le=1.0)
    region_code: Optional[str] = Field(None, max_length=10)
    active: bool = True


class MemberCreate(MemberBase):
    pass


class MemberResponse(MemberBase):
    member_id: int

    model_config = ConfigDict(from_attributes=True)


# === Sprint Schemas ===

class SprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that end_date >= start_date"""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be >= start_date')
        return v


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[SprintStatus] = None


class SprintResponse(SprintBase):
    sprint_id: int
    status: SprintStatus
    # Optional statistics
    member_count: Optional[int] = None
    total_capacity_hours: Optional[float] = None
    working_days: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# === Sprint Roster Schemas ===

class SprintRosterBase(BaseModel):
    allocation: Decimal = Field(..., gt=0.0, le=1.0)
    assignment_from: Optional[date] = None
    assignment_to: Optional[date] = None

    @field_validator('assignment_to')
    @classmethod
    def validate_assignment_dates(cls, v, info):
        """Validate that assignment_to >= assignment_from"""
        if v is not None and 'assignment_from' in info.data and info.data['assignment_from'] is not None:
            if v < info.data['assignment_from']:
                raise ValueError('assignment_to must be >= assignment_from')
        return v


class SprintRosterCreate(SprintRosterBase):
    member_id: int


class SprintRosterUpdate(SprintRosterBase):
    pass


class SprintRosterResponse(SprintRosterBase):
    sprint_id: int
    member_id: int
    member_name: Optional[str] = None  # Wird bei Joins befüllt

    model_config = ConfigDict(from_attributes=True)


# === PTO Schemas ===

class PTOBase(BaseModel):
    from_date: date
    to_date: date
    type: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('to_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that to_date >= from_date"""
        if 'from_date' in info.data and v < info.data['from_date']:
            raise ValueError('to_date must be >= from_date')
        return v


class PTOCreate(PTOBase):
    member_id: int


class PTOResponse(PTOBase):
    pto_id: int
    member_id: int
    member_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# === Holiday Schemas ===

class HolidayBase(BaseModel):
    date: date
    region_code: str = Field(..., max_length=10)
    name: str = Field(..., min_length=1, max_length=255)
    is_company_day: bool = True


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    holiday_id: int

    model_config = ConfigDict(from_attributes=True)


# === Availability Schemas ===

class AvailabilityDay(BaseModel):
    """Ein Tag in der Availability-Matrix"""
    date: date
    auto_state: str  # available|unavailable|half|weekend|holiday|pto|out_of_assignment
    override_state: Optional[AvailabilityState] = None
    final_state: AvailabilityState  # available|unavailable|half
    is_weekend: bool
    is_holiday: bool
    is_pto: bool
    in_assignment: bool


class AvailabilityMember(BaseModel):
    """Availability-Daten für ein Member"""
    member_id: int
    name: str
    employment_ratio: Decimal
    allocation: Decimal
    allocation_percentage: Optional[int] = None  # Already formatted as percentage
    days: List[AvailabilityDay]
    sum_days: float
    sum_hours: float


class AvailabilityResponse(BaseModel):
    """Complete Availability Response"""
    sprint: SprintResponse
    members: List[AvailabilityMember]
    sum_days_team: float
    sum_hours_team: float
    team_summary: Optional[dict] = None  # {"total_days": float, "total_hours": float}
    working_days: Optional[int] = None
    holidays_by_region: Optional[List[dict]] = None  # [{"region": str, "count": int}]
    available_capacity_hours: Optional[float] = None
    available_capacity_days: Optional[float] = None
    efficiency_percentage: Optional[int] = None


# === Availability Override Schemas ===

class AvailabilityOverrideBase(BaseModel):
    day: date
    state: AvailabilityState
    reason: Optional[str] = Field(None, max_length=500)


class AvailabilityOverrideCreate(AvailabilityOverrideBase):
    member_id: int


class AvailabilityOverrideUpdate(BaseModel):
    """Für PATCH: state=None zum Löschen"""
    state: Optional[AvailabilityState] = None
    reason: Optional[str] = Field(None, max_length=500)


class AvailabilityOverridePatch(BaseModel):
    """PATCH /sprints/{id}/availability Body"""
    member_id: int
    day: date
    state: Optional[AvailabilityState] = None  # None = delete override
    reason: Optional[str] = Field(None, max_length=500)


class AvailabilityOverrideResponse(AvailabilityOverrideBase):
    sprint_id: int
    member_id: int
    member_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# === PTO (Personal Time Off) Schemas ===

class PTOBase(BaseModel):
    member_id: int
    from_date: date
    to_date: date
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('to_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that to_date >= from_date"""
        if 'from_date' in info.data and v < info.data['from_date']:
            raise ValueError('to_date must be >= from_date')
        return v


class PTOCreate(PTOBase):
    pass


class PTOUpdate(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)


class PTO(PTOBase):
    pto_id: int
    member_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
