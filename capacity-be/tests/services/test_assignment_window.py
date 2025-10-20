"""
Tests für Assignment-Fenster Logik

Test Case 3: Assignment-Fenster
"""
import pytest
from datetime import date
from app.services.availability import AvailabilityService
from app.services.validation import ValidationService, ValidationError
from app.db.models import Member, Sprint, SprintRoster, AvailabilityState


class TestAssignmentWindow:
    """Test Assignment-Fenster Funktionalität"""
    
    def test_assignment_window_validation(self, db_session, sample_members, sample_sprint):
        """Test: Assignment-Fenster muss innerhalb Sprint-Grenzen liegen"""
        validator = ValidationService(db_session)
        
        # Case 1: assignment_from vor Sprint-Start
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_assignment_window(
                sprint_id=sample_sprint.sprint_id,
                assignment_from=date(2025, 10, 25),  # Vor Sprint-Start (27.10.)
                assignment_to=date(2025, 11, 5)
            )
        
        assert "cannot be before sprint start" in str(exc_info.value)
        
        # Case 2: assignment_to nach Sprint-Ende
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_assignment_window(
                sprint_id=sample_sprint.sprint_id,
                assignment_from=date(2025, 10, 30),
                assignment_to=date(2025, 11, 10)  # Nach Sprint-Ende (07.11.)
            )
        
        assert "cannot be after sprint end" in str(exc_info.value)
        
        # Case 3: assignment_to < assignment_from
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_assignment_window(
                sprint_id=sample_sprint.sprint_id,
                assignment_from=date(2025, 11, 5),
                assignment_to=date(2025, 11, 2)  # Früher als from
            )
        
        assert "assignment end must be >= assignment start" in str(exc_info.value).lower()
    
    def test_assignment_window_valid_cases(self, db_session, sample_members, sample_sprint):
        """Test: Gültige Assignment-Fenster werden akzeptiert"""
        validator = ValidationService(db_session)
        
        # Case 1: Kompletter Sprint
        try:
            validator.validate_assignment_window(
                sprint_id=sample_sprint.sprint_id,
                assignment_from=date(2025, 10, 27),  # Sprint-Start
                assignment_to=date(2025, 11, 7)     # Sprint-Ende
            )
        except ValidationError:
            pytest.fail("Valid assignment window rejected")
        
        # Case 2: Teilbereich des Sprints
        try:
            validator.validate_assignment_window(
                sprint_id=sample_sprint.sprint_id,
                assignment_from=date(2025, 10, 29),  # Innerhalb Sprint
                assignment_to=date(2025, 11, 5)     # Innerhalb Sprint
            )
        except ValidationError:
            pytest.fail("Valid partial assignment window rejected")
        
        # Case 3: Kein Assignment-Fenster (None values)
        try:
            validator.validate_assignment_window(
                sprint_id=sample_sprint.sprint_id,
                assignment_from=None,
                assignment_to=None
            )
        except ValidationError:
            pytest.fail("No assignment window should be valid")
    
    def test_assignment_window_affects_availability(self, db_session, sample_members, sample_sprint):
        """Test: Assignment-Fenster beeinflusst Availability korrekt"""
        alice = sample_members[0]
        
        # Sprint Roster mit Assignment-Fenster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0,
            assignment_from=date(2025, 10, 30),  # Startet später
            assignment_to=date(2025, 11, 5)     # Endet früher
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        
        # Prüfe Tage vor Assignment-Start
        oct_28_data = next(d for d in alice_data.days if d.date == date(2025, 10, 28))
        assert oct_28_data.in_assignment is False
        assert oct_28_data.auto_state == "out_of_assignment"
        
        # Prüfe Tage nach Assignment-Ende
        nov_6_data = next(d for d in alice_data.days if d.date == date(2025, 11, 6))
        assert nov_6_data.in_assignment is False
        assert nov_6_data.auto_state == "out_of_assignment"
        
        # Prüfe Tage innerhalb Assignment
        nov_1_data = next(d for d in alice_data.days if d.date == date(2025, 11, 1))
        assert nov_1_data.in_assignment is True
        # Auto-state hängt von anderen Faktoren ab (Wochenende, Feiertage, etc.)
        if nov_1_data.date.weekday() < 5 and not nov_1_data.is_holiday:
            assert nov_1_data.auto_state == "available"
    
    def test_no_assignment_window_full_sprint(self, db_session, sample_members, sample_sprint):
        """Test: Kein Assignment-Fenster = ganzer Sprint verfügbar"""
        alice = sample_members[0]
        
        # Sprint Roster ohne Assignment-Fenster
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0,
            assignment_from=None,
            assignment_to=None
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        
        # Alle Tage sollten in_assignment = True haben
        for day_data in alice_data.days:
            assert day_data.in_assignment is True
            # out_of_assignment sollte nie vorkommen
            assert day_data.auto_state != "out_of_assignment"
    
    def test_assignment_window_capacity_calculation(self, db_session, sample_members, sample_sprint):
        """Test: Assignment-Fenster beeinflusst Kapazitätsberechnung"""
        alice = sample_members[0]
        
        # Sprint Roster mit begrenztem Assignment-Fenster (nur 3 Werktage)
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0,
            assignment_from=date(2025, 11, 3),  # Montag
            assignment_to=date(2025, 11, 5)     # Mittwoch
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        
        # Kapazität sollte nur für die 3 Werktage berechnet werden
        # (3 Tage * 1.0 employment_ratio * 1.0 allocation * 8 Stunden)
        expected_hours = 3 * 1.0 * 1.0 * 8.0
        
        assert alice_data.sum_days <= 3.0  # Maximal 3 Tage
        assert alice_data.sum_hours <= expected_hours