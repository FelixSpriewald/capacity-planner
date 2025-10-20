"""CRUD Operations für Sprints"""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.sprints import Sprint, SprintStatus
from app.db.models.sprint_roster import SprintRoster
from app.schemas.schemas import SprintCreate, SprintUpdate


def calculate_status_from_dates(start_date: date, end_date: date) -> SprintStatus:
    """Calculate sprint status based on current date and sprint dates"""
    today = date.today()

    if today < start_date:
        return SprintStatus.PLANNED
    elif start_date <= today <= end_date:
        return SprintStatus.ACTIVE
    else:
        return SprintStatus.FINISHED


def calculate_working_days(start_date: date, end_date: date) -> int:
    """Calculate working days (excluding weekends) between two dates"""
    working_days = 0
    current_date = start_date

    while current_date <= end_date:
        # Monday = 0, Sunday = 6
        if current_date.weekday() < 5:  # Monday to Friday
            working_days += 1
        current_date += timedelta(days=1)

    return working_days


def get_sprint_statistics(db: Session, sprint: Sprint) -> dict:
    """Get statistics for a sprint including member count and capacity"""
    # Get roster count and total allocation
    roster_stats = db.query(
        func.count(SprintRoster.member_id).label('member_count'),
        func.sum(SprintRoster.allocation).label('total_allocation')
    ).filter(SprintRoster.sprint_id == sprint.sprint_id).first()

    member_count = roster_stats.member_count or 0
    total_allocation = float(roster_stats.total_allocation or 0)

    # Calculate working days
    working_days = calculate_working_days(sprint.start_date, sprint.end_date)

    # Calculate total capacity hours (assuming 8 hours per day)
    total_capacity_hours = total_allocation * working_days * 8

    return {
        'member_count': member_count,
        'total_capacity_hours': total_capacity_hours,
        'working_days': working_days
    }


def get_sprints(db: Session, skip: int = 0, limit: int = 100, include_stats: bool = True) -> List[Sprint]:
    """Alle Sprints abrufen mit automatischer Status-Aktualisierung und optionalen Statistiken"""
    sprints = db.query(Sprint).offset(skip).limit(limit).all()

    # Update status for all sprints based on current date
    for sprint in sprints:
        calculated_status = calculate_status_from_dates(sprint.start_date, sprint.end_date)
        if sprint.status != calculated_status:
            sprint.status = calculated_status

        # Add statistics if requested
        if include_stats:
            stats = get_sprint_statistics(db, sprint)
            sprint.member_count = stats['member_count']
            sprint.total_capacity_hours = stats['total_capacity_hours']
            sprint.working_days = stats['working_days']

    db.commit()
    return sprints


def get_sprint(db: Session, sprint_id: int, include_stats: bool = True) -> Optional[Sprint]:
    """Ein Sprint by ID mit automatischer Status-Aktualisierung und optionalen Statistiken"""
    sprint = db.query(Sprint).filter(Sprint.sprint_id == sprint_id).first()

    if sprint:
        calculated_status = calculate_status_from_dates(sprint.start_date, sprint.end_date)
        if sprint.status != calculated_status:
            sprint.status = calculated_status
            db.commit()

        # Add statistics if requested
        if include_stats:
            stats = get_sprint_statistics(db, sprint)
            sprint.member_count = stats['member_count']
            sprint.total_capacity_hours = stats['total_capacity_hours']
            sprint.working_days = stats['working_days']

    return sprint


def create_sprint(db: Session, sprint: SprintCreate) -> Sprint:
    """Neuen Sprint erstellen mit automatischer Status-Berechnung"""
    # Calculate initial status based on dates
    status = calculate_status_from_dates(sprint.start_date, sprint.end_date)

    db_sprint = Sprint(
        **sprint.model_dump(),
        status=status
    )
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint


def update_sprint(db: Session, sprint_id: int, sprint_update: SprintUpdate) -> Optional[Sprint]:
    """Sprint aktualisieren mit automatischer Status-Berechnung"""
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return None

    update_data = sprint_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_sprint, field):
            setattr(db_sprint, field, value)

    # Recalculate status if dates were changed
    if 'start_date' in update_data or 'end_date' in update_data or 'status' in update_data:
        db_sprint.status = calculate_status_from_dates(db_sprint.start_date, db_sprint.end_date)

    db.commit()
    db.refresh(db_sprint)
    return db_sprint


def update_all_sprint_statuses(db: Session) -> int:
    """Update all sprint statuses based on current date"""
    sprints = db.query(Sprint).all()
    updated_count = 0

    for sprint in sprints:
        new_status = calculate_status_from_dates(sprint.start_date, sprint.end_date)
        if sprint.status != new_status:
            sprint.status = new_status
            updated_count += 1

    if updated_count > 0:
        db.commit()

    return updated_count


def delete_sprint(db: Session, sprint_id: int) -> bool:
    """Sprint löschen"""
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return False

    db.delete(db_sprint)
    db.commit()
    return True
