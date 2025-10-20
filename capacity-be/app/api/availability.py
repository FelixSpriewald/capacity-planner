"""
Availability API Routes
"""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.services.availability import AvailabilityService
from app.schemas.schemas import (
    AvailabilityResponse, AvailabilityOverridePatch
)

router = APIRouter()


@router.get("/{sprint_id}/availability", response_model=AvailabilityResponse)
def get_sprint_availability(sprint_id: int, db: Session = Depends(get_db)):
    """
    Availability-Matrix für einen Sprint abrufen

    Liefert für alle Roster-Members:
    - Auto-Status (weekend/holiday/pto/out_of_assignment/available)
    - Override-Status
    - Final-Status (mit Override-Priorität)
    - Kapazitätssummen (Tage & Stunden)
    """
    service = AvailabilityService(db)
    availability = service.get_sprint_availability(sprint_id)

    if not availability:
        raise HTTPException(status_code=404, detail="Sprint not found")

    return availability


@router.patch("/{sprint_id}/availability")
def patch_sprint_availability(
    sprint_id: int,
    override_data: AvailabilityOverridePatch,
    db: Session = Depends(get_db)
):
    """
    Einzelne Availability-Override setzen/löschen

    Body:
    {
        "member_id": 1,
        "day": "2025-10-30",
        "state": "half",  // oder null zum Löschen
        "reason": "Arzttermin"
    }
    """
    # Sprint existiert prüfen
    service = AvailabilityService(db)
    availability = service.get_sprint_availability(sprint_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Sprint not found")

    # Tag muss im Sprint-Zeitraum liegen
    sprint = availability.sprint
    if not (sprint.start_date <= override_data.day <= sprint.end_date):
        raise HTTPException(
            status_code=422,
            detail=f"Day {override_data.day} is not within sprint range"
        )

    # Member muss im Roster sein
    member_ids = {m.member_id for m in availability.members}
    if override_data.member_id not in member_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Member {override_data.member_id} is not in sprint roster"
        )

    # Override setzen/löschen
    success = service.set_availability_override(
        sprint_id=sprint_id,
        member_id=override_data.member_id,
        day=override_data.day,
        state=override_data.state,
        reason=override_data.reason
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update override")

    return {"message": "Override updated successfully"}


@router.patch("/{sprint_id}/availability/bulk")
def patch_sprint_availability_bulk(
    sprint_id: int,
    overrides_data: List[AvailabilityOverridePatch],
    db: Session = Depends(get_db)
):
    """
    Bulk-Update für mehrere Availability-Overrides

    Body: Array von Override-Objekten
    """
    service = AvailabilityService(db)
    availability = service.get_sprint_availability(sprint_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Sprint not found")

    sprint = availability.sprint
    member_ids = {m.member_id for m in availability.members}

    results = []
    errors = []

    for i, override_data in enumerate(overrides_data):
        try:
            # Validierungen
            if not (sprint.start_date <= override_data.day <= sprint.end_date):
                errors.append(f"Item {i}: Day {override_data.day} not in sprint range")
                continue

            if override_data.member_id not in member_ids:
                errors.append(f"Item {i}: Member {override_data.member_id} not in roster")
                continue

            # Override setzen
            success = service.set_availability_override(
                sprint_id=sprint_id,
                member_id=override_data.member_id,
                day=override_data.day,
                state=override_data.state,
                reason=override_data.reason
            )

            if success:
                results.append(f"Item {i}: Updated successfully")
            else:
                errors.append(f"Item {i}: Failed to update")

        except Exception as e:
            errors.append(f"Item {i}: {str(e)}")

    return {
        "message": f"Processed {len(overrides_data)} items",
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors
    }
