"""
Tests für Kapazitätsberechnungen

Test Case 5: Summenbildung (Tage/Stunden) mit employment_ratio und allocation
"""
import pytest
from datetime import date
from app.services.availability import AvailabilityService
from app.db.models import Member, Sprint, SprintRoster, AvailabilityOverride, AvailabilityState


class TestCapacityCalculation:
    """Test Kapazitätsberechnungen mit employment_ratio und allocation"""
    
    def test_basic_capacity_calculation(self, db_session, sample_members, sample_sprint):
        """Test: Grundlegende Kapazitätsberechnung für Vollzeit-Member"""
        alice = next(m for m in sample_members if m.employment_ratio == 1.0)  # Alice: 100%
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0  # 100% allocation
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)
        
        # Sprint: 27.10. bis 07.11. = 12 Tage total
        # Workdays: 27.10.(Mo), 28.10.(Di), 29.10.(Mi), 30.10.(Do), 31.10.(Fr), 01.11.(Sa), 02.11.(So), 03.11.(Mo), 04.11.(Di), 05.11.(Mi), 06.11.(Do), 07.11.(Fr)
        # Werktage (Mo-Fr): 27,28,29,30,31 Okt + 03,04,05,06,07 Nov = 10 Werktage
        
        expected_workdays = 10
        expected_hours = expected_workdays * 1.0 * 1.0 * 8.0  # 10 * employment_ratio * allocation * 8h
        
        assert alice_data.sum_days == expected_workdays
        assert alice_data.sum_hours == expected_hours
    
    def test_part_time_capacity_calculation(self, db_session, sample_members, sample_sprint):
        """Test: Kapazitätsberechnung für Teilzeit-Member"""
        bogdan = next(m for m in sample_members if m.employment_ratio == 0.75)  # Bogdan: 75%
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=bogdan.member_id,
            allocation=1.0  # 100% allocation vom Sprint
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        bogdan_data = next(m for m in availability.members if m.member_id == bogdan.member_id)
        
        # 10 verfügbare Werktage (sum_days = RAW-Tage ohne employment_ratio)
        # sum_hours: 10 * 8h * 0.75 employment_ratio * 1.0 allocation = 60.0 Stunden
        expected_days = 10.0
        expected_hours = 10.0 * 8.0 * 0.75 * 1.0  # 60.0 Stunden
        
        assert bogdan_data.sum_days == expected_days
        assert bogdan_data.sum_hours == expected_hours
    
    def test_partial_allocation_capacity(self, db_session, sample_members, sample_sprint):
        """Test: Kapazitätsberechnung mit reduzierter Sprint-Allocation"""
        carol = next(m for m in sample_members if m.employment_ratio == 0.5)  # Carol: 50%
        
        # Sprint Roster mit 60% allocation hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=carol.member_id,
            allocation=0.6  # Nur 60% für diesen Sprint
        )
        db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        carol_data = next(m for m in availability.members if m.member_id == carol.member_id)

        # 10 Werktage (raw days) - sum_days ist immer raw verfügbare Tage
        expected_days = 10.0
        # sum_hours = 10 * 8h * 0.5 employment_ratio * 0.6 allocation = 24.0 Stunden
        expected_hours = 10.0 * 8.0 * 0.5 * 0.6  # 24.0 Stunden

        assert carol_data.sum_days == expected_days
        assert carol_data.sum_hours == expected_hours
    
    def test_overrides_affect_capacity(self, db_session, sample_members, sample_sprint):
        """Test: Overrides beeinflussen Kapazitätsberechnung"""
        alice = next(m for m in sample_members if m.employment_ratio == 1.0)
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        
        # Overrides hinzufügen
        overrides = [
            AvailabilityOverride(
                sprint_id=sample_sprint.sprint_id,
                member_id=alice.member_id,
                day=date(2025, 10, 28),  # Montag -> half
                state=AvailabilityState.HALF
            ),
            AvailabilityOverride(
                sprint_id=sample_sprint.sprint_id,
                member_id=alice.member_id,
                day=date(2025, 10, 29),  # Dienstag -> unavailable
                state=AvailabilityState.UNAVAILABLE
            )
        ]
        
        for override in overrides:
            db_session.add(override)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)

        # Original: 10 Werktage (raw days)
        # Änderungen: -0.5 (half) -1.0 (unavailable) = -1.5 Tage
        # Ergebnis: 10.0 - 1.5 = 8.5 Tage
        expected_days = 8.5
        expected_hours = expected_days * 8.0  # 8.5 * 8 = 68.0 Stunden

        assert alice_data.sum_days == expected_days
        assert alice_data.sum_hours == expected_hours
    
    def test_team_capacity_sum(self, db_session, sample_members, sample_sprint):
        """Test: Team-Gesamtkapazität berechnung"""
        # Alle Member ins Roster
        for member in sample_members:
            roster = SprintRoster(
                sprint_id=sample_sprint.sprint_id,
                member_id=member.member_id,
                allocation=1.0
            )
            db_session.add(roster)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        # Erwartete Individual-Kapazitäten:
        # Alice: 10 Werktage (raw days), 10 * 8 * 1.0 = 80 Stunden
        # Bogdan: 10 Werktage (raw days), 10 * 8 * 0.75 = 60 Stunden 
        # Carol: 10 Werktage (raw days), 10 * 8 * 0.5 = 40 Stunden
        # Team Gesamt: 30 raw days, 180 Stunden

        expected_team_days = 10.0 + 10.0 + 10.0  # 30.0 raw days
        expected_team_hours = 80.0 + 60.0 + 40.0  # 180.0 Stunden

        assert availability.sum_days_team == expected_team_days
        assert availability.sum_hours_team == expected_team_hours
        
        # Prüfe dass Individual-Summen korrekt sind
        individual_days_sum = sum(m.sum_days for m in availability.members)
        individual_hours_sum = sum(m.sum_hours for m in availability.members)
        
        assert individual_days_sum == expected_team_days
        assert individual_hours_sum == expected_team_hours
    
    def test_weekend_override_adds_capacity(self, db_session, sample_members, sample_sprint):
        """Test: Wochenend-Override erhöht Kapazität"""
        alice = next(m for m in sample_members if m.employment_ratio == 1.0)
        
        # Sprint Roster hinzufügen
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        
        # Samstag als verfügbar markieren
        saturday = date(2025, 11, 1)  # 1. November 2025 ist ein Samstag
        override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=saturday,
            state=AvailabilityState.AVAILABLE,
            reason="Samstag-Sprint"
        )
        db_session.add(override)
        db_session.commit()
        
        # Test: Availability Service
        service = AvailabilityService(db_session)
        availability = service.get_sprint_availability(sample_sprint.sprint_id)
        
        alice_data = next(m for m in availability.members if m.member_id == alice.member_id)

        # Normal: 10 Werktage + 1 Samstag (override) = 11 Tage
        expected_days = 11.0
        expected_hours = expected_days * 8.0  # 88.0 Stunden

        assert alice_data.sum_days == expected_days
        assert alice_data.sum_hours == expected_hours