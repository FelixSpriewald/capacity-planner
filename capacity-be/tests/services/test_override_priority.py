"""
Tests für Override-Priorität

Test Case 4: Overrides-Priorität
"""
import pytest
from datetime import date
from app.services.availability import AvailabilityService
from app.db.models import Member, Sprint, SprintRoster, AvailabilityOverride, PTO, Holiday, AvailabilityState


class TestOverridePriority:
    """Test Override-Priorität über Auto-Status"""
    
    def test_override_beats_weekend(self, db_session, sample_members, sample_sprint):
        """Test: Override überschreibt Wochenende"""
        alice = sample_members[0]
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        
        # Override für Samstag (normalerweise weekend)
        saturday = date(2025, 11, 1)  # 1. November 2025 ist ein Samstag
        override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=saturday,
            state=AvailabilityState.AVAILABLE,
            reason="Wochenendarbeit"
        )
        db_session.add(override)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        saturday_data = next(d for d in alice_data.days if d.date == saturday)
        
        # Assertions
        assert saturday_data.is_weekend is True  # Immer noch erkannt als Wochenende
        assert saturday_data.auto_state == "weekend"  # Auto-Status bleibt
        assert saturday_data.override_state == AvailabilityState.AVAILABLE  # Override gesetzt
        assert saturday_data.final_state == AvailabilityState.AVAILABLE  # Override gewinnt
    
    def test_override_beats_holiday(self, db_session, sample_members, sample_sprint):
        """Test: Override überschreibt Feiertag"""
        alice = next(m for m in sample_members if m.region_code == "DE-NW")

        # Holiday hinzufügen - 3. November 2025 ist ein Montag
        holiday = Holiday(
            name="Allerheiligen ersatz",
            date=date(2025, 11, 3),
            region_code="DE-NW"
        )
        db_session.add(holiday)

        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)

        # Override für Feiertag
        override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=date(2025, 11, 3),
            state=AvailabilityState.HALF,
            reason="Notfall-Einsatz"
        )
        db_session.add(override)
        db_session.commit()

        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)

        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        holiday_data = next(d for d in alice_data.days if d.date == date(2025, 11, 3))

        # Assertions
        assert holiday_data.is_holiday is True  # Immer noch Feiertag
        assert holiday_data.auto_state == "holiday"  # Auto-Status bleibt
        assert holiday_data.override_state == AvailabilityState.HALF  # Override gesetzt
        assert holiday_data.final_state == AvailabilityState.HALF  # Override gewinnt
    
    def test_override_beats_pto(self, db_session, sample_members, sample_sprint):
        """Test: Override überschreibt PTO"""
        alice = sample_members[0]
        
        # PTO hinzufügen
        pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 3),
            to_date=date(2025, 11, 5),
            notes="Urlaub"
        )
        db_session.add(pto)
        
        # Sprint Roster hinzufügen  
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        
        # Override für PTO-Tag
        override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=date(2025, 11, 4),
            state=AvailabilityState.AVAILABLE,
            reason="Dringender Termin"
        )
        db_session.add(override)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        pto_day_data = next(d for d in alice_data.days if d.date == date(2025, 11, 4))
        
        # Assertions
        assert pto_day_data.is_pto is True  # PTO erkannt
        assert pto_day_data.auto_state == "pto"  # Auto-Status bleibt
        assert pto_day_data.override_state == AvailabilityState.AVAILABLE  # Override gesetzt
        assert pto_day_data.final_state == AvailabilityState.AVAILABLE  # Override gewinnt
    
    def test_override_removal_restores_auto(self, db_session, sample_members, sample_sprint):
        """Test: Override-Entfernung stellt Auto-Status wieder her"""
        alice = sample_members[0]
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        
        # Schritt 1: Normaler Zustand (kein Override)
        availability1 = service.get_sprint_availability(sample_sprint.sprint_id)
        alice_data1 = next(m for m in availability1.members if m.member_id == alice.member_id)
        workday_data1 = next(d for d in alice_data1.days if d.date.weekday() < 5 and not d.is_holiday)
        
        original_state = workday_data1.final_state  # Store as Enum
        original_auto_state = workday_data1.auto_state  # Store as string
        assert workday_data1.override_state is None
        assert workday_data1.final_state == original_state
        
        # Schritt 2: Override setzen
        override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=workday_data1.date,
            state=AvailabilityState.UNAVAILABLE,
            reason="Arzttermin"
        )
        db_session.add(override)
        db_session.commit()
        
        availability2 = service.get_sprint_availability(sample_sprint.sprint_id)
        alice_data2 = next(m for m in availability2.members if m.member_id == alice.member_id)
        workday_data2 = next(d for d in alice_data2.days if d.date == workday_data1.date)
        
        assert workday_data2.auto_state == original_auto_state  # Auto-Status unverändert
        assert workday_data2.override_state == AvailabilityState.UNAVAILABLE  # Override gesetzt
        assert workday_data2.final_state == AvailabilityState.UNAVAILABLE  # Override aktiv
        
        # Schritt 3: Override entfernen
        db_session.delete(override)
        db_session.commit()

        availability3 = service.get_sprint_availability(sample_sprint.sprint_id)
        alice_data3 = next(m for m in availability3.members if m.member_id == alice.member_id)
        workday_data3 = next(d for d in alice_data3.days if d.date == workday_data1.date)
        
        assert workday_data3.auto_state == original_auto_state  # Auto-Status gleich
        assert workday_data3.override_state is None  # Kein Override
        assert workday_data3.final_state == original_state  # Auto-Status wieder aktiv
    
    def test_multiple_overrides_same_member(self, db_session, sample_members, sample_sprint):
        """Test: Mehrere Overrides für den gleichen Member"""
        alice = sample_members[0]
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        
        # Mehrere Overrides hinzufügen
        overrides = [
            AvailabilityOverride(
                sprint_id=sample_sprint.sprint_id,
                member_id=alice.member_id,
                day=date(2025, 10, 29),
                state=AvailabilityState.HALF,
                reason="Termin am Vormittag"
            ),
            AvailabilityOverride(
                sprint_id=sample_sprint.sprint_id,
                member_id=alice.member_id,
                day=date(2025, 10, 30),
                state=AvailabilityState.UNAVAILABLE,
                reason="Fortbildung"
            ),
            AvailabilityOverride(
                sprint_id=sample_sprint.sprint_id,
                member_id=alice.member_id,
                day=date(2025, 10, 31),
                state=AvailabilityState.AVAILABLE,
                reason="Samstag-Arbeit"
            )
        ]
        
        for override in overrides:
            db_session.add(override)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        
        # Jeder Override-Tag sollte korrekt gesetzt sein
        day_29 = next(d for d in alice_data.days if d.date == date(2025, 10, 29))
        day_30 = next(d for d in alice_data.days if d.date == date(2025, 10, 30))
        day_31 = next(d for d in alice_data.days if d.date == date(2025, 10, 31))
        
        assert day_29.final_state == AvailabilityState.HALF
        assert day_30.final_state == AvailabilityState.UNAVAILABLE
        assert day_31.final_state == AvailabilityState.AVAILABLE
        
        # Überprüfe dass Overrides korrekt gesetzt sind
        assert day_29.override_state == AvailabilityState.HALF
        assert day_30.override_state == AvailabilityState.UNAVAILABLE
        assert day_31.override_state == AvailabilityState.AVAILABLE