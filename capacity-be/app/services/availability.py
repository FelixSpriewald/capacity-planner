"""
Availability Business Logic Service

Berechnet für einen Sprint die Verfügbarkeit aller Roster-Members
tag-genau mit Auto-Status + Overrides + Kapazitätssummen.
"""
from datetime import date, timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    Sprint, SprintRoster, Member, Holiday, PTO,
    AvailabilityOverride, AvailabilityState
)
from app.schemas.schemas import (
    AvailabilityResponse, AvailabilityMember, AvailabilityDay, SprintResponse
)


class AvailabilityService:
    """Service für Availability-Berechnungen"""

    def __init__(self, db: Session):
        self.db = db

    def get_sprint_availability(self, sprint_id: int) -> Optional[AvailabilityResponse]:
        """
        Hauptmethode: Berechnet komplette Availability-Matrix für Sprint
        """
        # Sprint laden
        sprint = self.db.query(Sprint).filter(Sprint.sprint_id == sprint_id).first()
        if not sprint:
            return None

        # Sprint Roster mit Members laden
        roster_entries = self.db.query(SprintRoster).options(
            joinedload(SprintRoster.member)
        ).filter(SprintRoster.sprint_id == sprint_id).all()

        if not roster_entries:
            # Leerer Sprint
            return AvailabilityResponse(
                sprint=SprintResponse.model_validate(sprint),
                members=[],
                sum_days_team=0.0,
                sum_hours_team=0.0
            )

        # Alle Tage im Sprint
        sprint_days = self._generate_sprint_days(sprint.start_date, sprint.end_date)

        # Feiertage laden (alle Regionen im Roster)
        region_codes = {entry.member.region_code for entry in roster_entries if entry.member.region_code}
        holidays_map = self._load_holidays(sprint_days, region_codes)

        # PTO laden
        member_ids = [entry.member_id for entry in roster_entries]
        pto_map = self._load_pto(sprint_days, member_ids)

        # Overrides laden
        overrides_map = self._load_overrides(sprint_id, member_ids, sprint_days)

        # Für jeden Member Availability berechnen
        members_data = []
        total_team_days = 0.0
        total_team_hours = 0.0

        for roster_entry in roster_entries:
            member_data = self._calculate_member_availability(
                roster_entry, sprint_days, holidays_map, pto_map, overrides_map
            )
            members_data.append(member_data)
            total_team_days += member_data.sum_days
            total_team_hours += member_data.sum_hours

        # Calculate additional metrics
        working_days = self._calculate_working_days(sprint.start_date, sprint.end_date)
        holidays_by_region = self._calculate_holidays_by_region(roster_entries, holidays_map, sprint_days)
        total_capacity_hours = self._calculate_total_capacity_hours(roster_entries, working_days)
        total_capacity_days = self._calculate_total_capacity_days(roster_entries, working_days)
        available_capacity_hours = self._calculate_available_capacity_hours(members_data)
        available_capacity_days = self._calculate_available_capacity_days(members_data)
        efficiency = self._calculate_efficiency(available_capacity_hours, total_capacity_hours)

        return AvailabilityResponse(
            sprint=SprintResponse.model_validate(sprint),
            members=members_data,
            sum_days_team=total_team_days,
            sum_hours_team=total_team_hours,
            team_summary={
                "total_days": total_capacity_days,
                "total_hours": total_capacity_hours
            },
            working_days=working_days,
            holidays_by_region=holidays_by_region,
            available_capacity_hours=available_capacity_hours,
            available_capacity_days=available_capacity_days,
            efficiency_percentage=efficiency
        )

    def _generate_sprint_days(self, start_date: date, end_date: date) -> List[date]:
        """Alle Tage im Sprint generieren"""
        days = []
        current = start_date
        while current <= end_date:
            days.append(current)
            current += timedelta(days=1)
        return days

    def _load_holidays(self, sprint_days: List[date], region_codes: set) -> Dict[tuple, Holiday]:
        """Feiertage laden: (date, region_code) -> Holiday"""
        if not region_codes:
            return {}

        holidays = self.db.query(Holiday).filter(
            Holiday.date.in_(sprint_days),
            Holiday.region_code.in_(region_codes)
        ).all()

        return {(h.date, h.region_code): h for h in holidays}

    def _load_pto(self, sprint_days: List[date], member_ids: List[int]) -> Dict[tuple, PTO]:
        """PTO laden: (member_id, date) -> PTO"""
        if not member_ids:
            return {}

        start_date = min(sprint_days)
        end_date = max(sprint_days)

        # PTO-Einträge laden die den Sprint überlappen
        pto_entries = self.db.query(PTO).filter(
            PTO.member_id.in_(member_ids),
            PTO.from_date <= end_date,
            PTO.to_date >= start_date
        ).all()

        # Für jeden PTO-Eintrag alle betroffenen Tage mappen
        pto_map = {}
        for pto in pto_entries:
            current = max(pto.from_date, start_date)
            end = min(pto.to_date, end_date)

            while current <= end:
                pto_map[(pto.member_id, current)] = pto
                current += timedelta(days=1)

        return pto_map

    def _load_overrides(self, sprint_id: int, member_ids: List[int], sprint_days: List[date]) -> Dict[tuple, AvailabilityOverride]:
        """Overrides laden: (member_id, date) -> AvailabilityOverride"""
        if not member_ids:
            return {}

        overrides = self.db.query(AvailabilityOverride).filter(
            AvailabilityOverride.sprint_id == sprint_id,
            AvailabilityOverride.member_id.in_(member_ids),
            AvailabilityOverride.day.in_(sprint_days)
        ).all()

        return {(o.member_id, o.day): o for o in overrides}

    def _calculate_member_availability(
        self,
        roster_entry: SprintRoster,
        sprint_days: List[date],
        holidays_map: Dict[tuple, Holiday],
        pto_map: Dict[tuple, PTO],
        overrides_map: Dict[tuple, AvailabilityOverride]
    ) -> AvailabilityMember:
        """Availability für einen Member berechnen"""

        member = roster_entry.member
        days_data = []
        sum_days = 0.0

        for day in sprint_days:
            day_data = self._calculate_day_availability(
                member, roster_entry, day, holidays_map, pto_map, overrides_map
            )
            days_data.append(day_data)

            # Summe berechnen (mit Allocation berücksichtigen)
            if day_data.final_state == AvailabilityState.AVAILABLE:
                sum_days += float(roster_entry.allocation)
            elif day_data.final_state == AvailabilityState.HALF:
                sum_days += float(roster_entry.allocation) * 0.5

        # Stunden = Tage * 8h * employment_ratio * allocation
        sum_hours = float(sum_days * 8 * float(member.employment_ratio) * float(roster_entry.allocation))

        return AvailabilityMember(
            member_id=member.member_id,
            name=member.name,
            employment_ratio=member.employment_ratio,
            allocation=roster_entry.allocation,
            allocation_percentage=round(float(roster_entry.allocation) * 100),
            days=days_data,
            sum_days=sum_days,
            sum_hours=sum_hours
        )

    def _calculate_day_availability(
        self,
        member: Member,
        roster_entry: SprintRoster,
        day: date,
        holidays_map: Dict[tuple, Holiday],
        pto_map: Dict[tuple, PTO],
        overrides_map: Dict[tuple, AvailabilityOverride]
    ) -> AvailabilityDay:
        """Availability für einen einzelnen Tag berechnen"""

        # Basiswerte
        is_weekend = day.weekday() >= 5
        is_holiday = (day, member.region_code) in holidays_map if member.region_code else False
        is_pto = (member.member_id, day) in pto_map

        # Assignment-Fenster prüfen
        in_assignment = True
        if roster_entry.assignment_from and day < roster_entry.assignment_from:
            in_assignment = False
        if roster_entry.assignment_to and day > roster_entry.assignment_to:
            in_assignment = False

        # Auto-Status bestimmen
        if is_weekend:
            auto_state = "weekend"
        elif is_holiday:
            auto_state = "holiday"
        elif is_pto:
            auto_state = "pto"
        elif not in_assignment:
            auto_state = "out_of_assignment"
        else:
            auto_state = "available"

        # Override laden
        override = overrides_map.get((member.member_id, day))
        override_state = override.state if override else None

        # Final State bestimmen (Override hat Priorität)
        if override_state is not None:
            final_state = override_state
        elif auto_state in ["weekend", "holiday", "pto", "out_of_assignment"]:
            final_state = AvailabilityState.UNAVAILABLE
        else:
            final_state = AvailabilityState.AVAILABLE

        return AvailabilityDay(
            date=day,
            auto_state=auto_state,
            override_state=override_state,
            final_state=final_state,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            is_pto=is_pto,
            in_assignment=in_assignment
        )

    def set_availability_override(
        self,
        sprint_id: int,
        member_id: int,
        day: date,
        state: Optional[AvailabilityState],
        reason: Optional[str] = None
    ) -> bool:
        """
        Availability Override setzen oder löschen
        state=None → Override löschen
        """
        # Existing override suchen
        existing = self.db.query(AvailabilityOverride).filter(
            AvailabilityOverride.sprint_id == sprint_id,
            AvailabilityOverride.member_id == member_id,
            AvailabilityOverride.day == day
        ).first()

        if state is None:
            # Override löschen
            if existing:
                self.db.delete(existing)
                self.db.commit()
                return True
            return False  # Nichts zu löschen
        else:
            # Override setzen/updaten
            if existing:
                existing.state = state
                existing.reason = reason
            else:
                override = AvailabilityOverride(
                    sprint_id=sprint_id,
                    member_id=member_id,
                    day=day,
                    state=state,
                    reason=reason
                )
                self.db.add(override)

            self.db.commit()
            return True

    def _calculate_working_days(self, start_date: date, end_date: date) -> int:
        """Calculate working days (Monday to Friday) in sprint"""
        working_days = 0
        current = start_date
        while current <= end_date:
            # Monday = 0, Sunday = 6
            if current.weekday() < 5:  # Monday to Friday
                working_days += 1
            current += timedelta(days=1)
        return working_days

    def _calculate_holidays_by_region(self, roster_entries: List, holidays_map: Dict, sprint_days: List[date]) -> List[Dict]:
        """Calculate holidays count by region"""
        region_counts = {}

        for roster_entry in roster_entries:
            if not roster_entry.member.region_code:
                continue

            region = roster_entry.member.region_code
            holiday_count = 0

            for day in sprint_days:
                if (day, region) in holidays_map:
                    holiday_count += 1

            if holiday_count > 0:
                region_counts[region] = max(region_counts.get(region, 0), holiday_count)

        return [{'region': region, 'count': count} for region, count in region_counts.items()]

    def _calculate_total_capacity_hours(self, roster_entries: List, working_days: int) -> float:
        """Calculate total capacity hours for all members"""
        total = 0.0
        for roster_entry in roster_entries:
            member_capacity = (
                working_days * 8 *  # 8 hours per working day
                float(roster_entry.member.employment_ratio) *
                float(roster_entry.allocation)
            )
            total += member_capacity
        return round(total, 1)

    def _calculate_total_capacity_days(self, roster_entries: List, working_days: int) -> float:
        """Calculate total capacity days for all members"""
        total = 0.0
        for roster_entry in roster_entries:
            member_capacity = (
                working_days *
                float(roster_entry.member.employment_ratio) *
                float(roster_entry.allocation)
            )
            total += member_capacity
        return round(total, 1)

    def _calculate_available_capacity_hours(self, members_data: List) -> float:
        """Calculate available capacity hours from member data"""
        total = 0.0
        for member in members_data:
            total += member.sum_hours
        return round(total, 1)

    def _calculate_available_capacity_days(self, members_data: List) -> float:
        """Calculate available capacity days from member data"""
        total = 0.0
        for member in members_data:
            total += member.sum_days
        return round(total, 1)

    def _calculate_efficiency(self, available_hours: float, total_hours: float) -> int:
        """Calculate efficiency percentage"""
        if total_hours == 0:
            return 0
        return round((available_hours / total_hours) * 100)
