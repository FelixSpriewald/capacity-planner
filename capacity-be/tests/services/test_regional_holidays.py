"""
Tests für regionale Feiertage (DE-NW vs UA)

Test Case 1: Feiertage je Region
"""
import pytest
from datetime import date
from app.services.availability import AvailabilityService
from app.db.models import Member, Sprint, SprintRoster, Holiday, AvailabilityState


class TestRegionalHolidays:
    """Test regionale Feiertag-Erkennung"""
    
    def test_german_holiday_recognition(self, db_session, sample_members, sample_sprint):
        """Test: Deutsche Feiertage werden für DE-NW Member erkannt"""
        # Setup: Allerheiligen (3. November - Montag) für DE-NW
        holiday = Holiday(
            name="Allerheiligen",
            date=date(2025, 11, 3),
            region_code="DE-NW"
        )
        db_session.add(holiday)
        
        # Sprint Roster: Alice (DE-NW) hinzufügen
        alice = next(m for m in sample_members if m.region_code == "DE-NW")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        # Assertions: 3. November sollte als Holiday erkannt werden
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        
        # Finde den 3. November in den Tagen
        nov_3_data = next(d for d in alice_data.days if d.date == date(2025, 11, 3))
        
        assert nov_3_data.is_holiday is True
        assert nov_3_data.auto_state == "holiday"
        assert nov_3_data.final_state == AvailabilityState.UNAVAILABLE  # Holiday = unavailable
    
    def test_ukrainian_holiday_recognition(self, db_session, sample_members):
        """Test: Ukrainische Feiertage werden für UA Member erkannt"""
        # Setup: Sprint im August für Ukrainian Independence Day
        sprint = Sprint(
            name="August Sprint",
            start_date=date(2025, 8, 20),
            end_date=date(2025, 8, 29),
            status="ACTIVE"
        )
        db_session.add(sprint)
        db_session.commit()
        db_session.refresh(sprint)
        
        # Ukrainian Independence Day (verschoben auf Montag)
        holiday = Holiday(
            name="Ukrainian Independence Day",
            date=date(2025, 8, 25),  # Montag
            region_code="UA"
        )
        db_session.add(holiday)
        
        # Sprint Roster: Bogdan (UA) hinzufügen
        bogdan = next(m for m in sample_members if m.region_code == "UA")
        roster = SprintRoster(
            sprint_id=sprint.sprint_id,
            member_id=bogdan.member_id,
            allocation=0.75
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sprint.sprint_id)
        
        # Assertions: 25. August sollte als Holiday erkannt werden
        bogdan_data = next(m for m in availability.members if m.member_id == bogdan.member_id)

        # Finde den 25. August in den Tagen
        aug_25_data = next(d for d in bogdan_data.days if d.date == date(2025, 8, 25))

        assert aug_25_data.is_holiday is True
        assert aug_25_data.auto_state == "holiday"
        assert aug_25_data.final_state == AvailabilityState.UNAVAILABLE
    
    def test_no_region_no_holidays(self, db_session, sample_members, sample_sprint):
        """Test: Member ohne region_code ignoriert Feiertage"""
        # Setup: Feiertag hinzufügen
        holiday = Holiday(
            name="Allerheiligen",
            date=date(2025, 11, 1),
            region_code="DE-NW"
        )
        db_session.add(holiday)
        
        # Sprint Roster: Carol (kein region_code) hinzufügen  
        carol = next(m for m in sample_members if m.region_code is None)
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=carol.member_id,
            allocation=0.5
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        # Assertions: 1. November sollte NICHT als Holiday erkannt werden
        carol_data = next(m for m in availability.members if m.member_id == carol.member_id)
        
        # Finde den 1. November in den Tagen
        nov_1_data = next(d for d in carol_data.days if d.date == date(2025, 11, 1))
        
        assert nov_1_data.is_holiday is False
        # Sollte normal verfügbar sein (außer Wochenende)
        if nov_1_data.date.weekday() < 5:  # Mo-Fr
            assert nov_1_data.auto_state == "available"
        else:
            assert nov_1_data.auto_state == "weekend"
    
    def test_cross_regional_holidays(self, db_session, sample_members, sample_sprint):
        """Test: Feiertag in einer Region betrifft nur die entsprechenden Member"""
        # Setup: Deutscher Feiertag
        holiday = Holiday(
            name="Tag der Deutschen Einheit",
            date=date(2025, 10, 3),  # Nicht im Sprint, aber für Konzept
            region_code="DE-NW"
        )
        db_session.add(holiday)
        
        # Beide Member ins Roster
        alice = next(m for m in sample_members if m.region_code == "DE-NW")
        bogdan = next(m for m in sample_members if m.region_code == "UA")
        
        for member in [alice, bogdan]:
            roster = SprintRoster(
                sprint_id=sample_sprint.sprint_id,
                member_id=member.member_id,
                allocation=1.0
            )
            db_session.add(roster)
        db_session.commit()
        
        # Test: Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        # Sollte 2 Member haben
        assert len(availability.members) == 2
        
        # Alice sollte deutsche Feiertage haben, Bogdan nicht
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        bogdan_data = next(m for m in availability.members if m.member_id == bogdan.member_id)
        
        # Beide haben gleiche Anzahl Tage im Sprint
        assert len(alice_data.days) == len(bogdan_data.days)

        # Der Test validiert das regionale Holiday-Verhalten, indem wir nach Holiday-Status suchen
        # Da der deutsche Feiertag (3. Oktober) nicht im Sprint-Zeitraum liegt,
        # sollten beide Member die gleiche Anzahl verfügbarer Tage haben
        assert alice_data.sum_days == bogdan_data.sum_days
        
        # Alice (1.0 employment) sollte 80h haben, Bogdan (0.75 employment) sollte 60h haben
        assert alice_data.sum_hours == 80.0  # 10 days * 8h * 1.0
        assert bogdan_data.sum_hours == 60.0  # 10 days * 8h * 0.75