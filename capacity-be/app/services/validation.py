"""
Validation Service für Business Logic Validierungen

Erweiterte Validierungen die über einfache Pydantic Schema-Validierung hinausgehen.
"""
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import Sprint, Member, SprintRoster, PTO
from app.db.crud.sprints import get_sprint
from app.db.crud.members import get_member
from app.db.crud.sprint_roster import get_roster_entry


class ValidationError(Exception):
    """Custom Validation Error für Business Logic"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class ValidationService:
    """Service für erweiterte Business Logic Validierungen"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_sprint_dates(self, start_date: date, end_date: date):
        """
        Validate sprint dates
        - end_date >= start_date
        - Sprint sollte mindestens 1 Werktag haben
        """
        if end_date < start_date:
            raise ValidationError("End date must be >= start date", "end_date")
        
        # Prüfe ob mindestens 1 Werktag im Sprint
        current = start_date
        has_workday = False
        while current <= end_date:
            if current.weekday() < 5:  # Mo-Fr
                has_workday = True
                break
            current = current.replace(day=current.day + 1)
        
        if not has_workday:
            raise ValidationError("Sprint must contain at least one workday (Monday-Friday)", "start_date")
    
    def validate_roster_uniqueness(self, sprint_id: int, member_id: int, exclude_existing: bool = False):
        """
        Validate that member is not already in sprint roster
        """
        existing = get_roster_entry(self.db, sprint_id, member_id)
        
        if existing and not exclude_existing:
            sprint = get_sprint(self.db, sprint_id)
            member = get_member(self.db, member_id)
            sprint_name = sprint.name if sprint else f"Sprint {sprint_id}"
            member_name = member.name if member else f"Member {member_id}"
            
            raise ValidationError(
                f"Member '{member_name}' is already assigned to '{sprint_name}'",
                "member_id"
            )
    
    def validate_assignment_window(self, sprint_id: int, assignment_from: Optional[date], assignment_to: Optional[date]):
        """
        Validate assignment window is within sprint bounds
        """
        if assignment_from is None and assignment_to is None:
            return  # No assignment window = full sprint
        
        sprint = get_sprint(self.db, sprint_id)
        if not sprint:
            raise ValidationError(f"Sprint {sprint_id} not found", "sprint_id")
        
        if assignment_from and assignment_from < sprint.start_date:
            raise ValidationError(
                f"Assignment start ({assignment_from}) cannot be before sprint start ({sprint.start_date})",
                "assignment_from"
            )
        
        if assignment_to and assignment_to > sprint.end_date:
            raise ValidationError(
                f"Assignment end ({assignment_to}) cannot be after sprint end ({sprint.end_date})",
                "assignment_to"
            )
        
        if assignment_from and assignment_to and assignment_to < assignment_from:
            raise ValidationError(
                "Assignment end must be >= assignment start",
                "assignment_to"
            )
    
    def validate_pto_dates(self, member_id: int, from_date: date, to_date: date, exclude_pto_id: Optional[int] = None):
        """
        Validate PTO dates
        - to_date >= from_date (already in schema)
        - No overlapping PTO for same member
        """
        if to_date < from_date:
            raise ValidationError("PTO end date must be >= start date", "to_date")
        
        # Prüfe auf überlappende PTO-Einträge
        overlapping_pto = self.db.query(PTO).filter(
            PTO.member_id == member_id,
            PTO.from_date <= to_date,
            PTO.to_date >= from_date
        )
        
        if exclude_pto_id:
            overlapping_pto = overlapping_pto.filter(PTO.pto_id != exclude_pto_id)
        
        existing = overlapping_pto.first()
        if existing:
            member = get_member(self.db, member_id)
            member_name = member.name if member else f"Member {member_id}"
            
            raise ValidationError(
                f"PTO period overlaps with existing PTO for {member_name} ({existing.from_date} to {existing.to_date})",
                "from_date"
            )
    
    def validate_availability_override_date(self, sprint_id: int, day: date):
        """
        Validate that override date is within sprint bounds
        """
        sprint = get_sprint(self.db, sprint_id)
        if not sprint:
            raise ValidationError(f"Sprint {sprint_id} not found", "sprint_id")
        
        if not (sprint.start_date <= day <= sprint.end_date):
            raise ValidationError(
                f"Override date {day} is not within sprint range ({sprint.start_date} to {sprint.end_date})",
                "day"
            )
    
    def validate_member_in_roster(self, sprint_id: int, member_id: int):
        """
        Validate that member is in sprint roster
        """
        roster_entry = get_roster_entry(self.db, sprint_id, member_id)
        if not roster_entry:
            sprint = get_sprint(self.db, sprint_id)
            member = get_member(self.db, member_id)
            sprint_name = sprint.name if sprint else f"Sprint {sprint_id}"
            member_name = member.name if member else f"Member {member_id}"
            
            raise ValidationError(
                f"Member '{member_name}' is not assigned to '{sprint_name}'",
                "member_id"
            )
    
    def validate_allocation_range(self, allocation: float):
        """
        Validate allocation is in valid range (0, 1]
        """
        if allocation <= 0:
            raise ValidationError("Allocation must be greater than 0", "allocation")
        
        if allocation > 1:
            raise ValidationError("Allocation cannot be greater than 1.0 (100%)", "allocation")
    
    def validate_employment_ratio(self, employment_ratio: float):
        """
        Validate employment ratio is in valid range (0, 1]
        """
        if employment_ratio <= 0:
            raise ValidationError("Employment ratio must be greater than 0", "employment_ratio")
        
        if employment_ratio > 1:
            raise ValidationError("Employment ratio cannot be greater than 1.0 (100%)", "employment_ratio")