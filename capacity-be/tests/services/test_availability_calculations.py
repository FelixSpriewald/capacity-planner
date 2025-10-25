"""
Test-Datei für die neuen Backend-Berechnungsmethoden in AvailabilityService.
Diese Tests sind essentiell für die Qualitätssicherung der Kapazitätsplanung.
"""
import pytest
from datetime import date, timedelta
from app.services.availability import AvailabilityService
from app.db.models import Member, Sprint, SprintRoster


class TestAvailabilityCalculations:
    """Test-Suite für alle _calculate_* Methoden in AvailabilityService"""

    def test_calculate_working_days_simple_week(self, db_session):
        """Test: Arbeitstagberechnung für eine simple Woche (Mo-Fr)"""
        service = AvailabilityService(db_session)

        # Test 1: Eine vollständige Woche (Mo 27.10. - Fr 31.10.2025)
        start_date = date(2025, 10, 27)  # Montag
        end_date = date(2025, 10, 31)    # Freitag

        working_days = service._calculate_working_days(start_date, end_date)
        assert working_days == 5

    def test_calculate_working_days_with_weekend(self, db_session):
        """Test: Arbeitstagberechnung mit Wochenenden"""
        service = AvailabilityService(db_session)

        # Test 2: Zwei Wochen mit Wochenenden (Mo 27.10. - Fr 07.11.2025)
        start_date = date(2025, 10, 27)  # Montag
        end_date = date(2025, 11, 7)     # Freitag (nach Wochenende)

        working_days = service._calculate_working_days(start_date, end_date)
        # 1. Woche: Mo-Fr (5 Tage) + 2. Woche: Mo-Fr (5 Tage) = 10 Tage
        assert working_days == 10

    def test_calculate_working_days_single_day(self, db_session):
        """Test: Arbeitstagberechnung für einen einzelnen Tag"""
        service = AvailabilityService(db_session)

        # Test 3: Nur ein Montag
        monday = date(2025, 10, 27)
        working_days = service._calculate_working_days(monday, monday)
        assert working_days == 1

        # Test 4: Nur ein Samstag (sollte 0 sein)
        saturday = date(2025, 11, 1)  # Samstag
        working_days = service._calculate_working_days(saturday, saturday)
        assert working_days == 0

    def test_calculate_holidays_by_region(self, db_session, sample_members):
        """Test: Feiertagsberechnung nach Region"""
        service = AvailabilityService(db_session)

        # Mock roster_entries mit verschiedenen Regionen
        alice = next(m for m in sample_members if m.region_code == "DE-NW")
        bogdan = next(m for m in sample_members if m.region_code == "UA")

        # Simuliere Sprint Roster Entries
        class MockRosterEntry:
            def __init__(self, member):
                self.member = member

        roster_entries = [
            MockRosterEntry(alice),   # DE-NW region
            MockRosterEntry(bogdan),  # UA region
        ]

        # Mock holidays_map
        sprint_days = [
            date(2025, 10, 27),
            date(2025, 10, 28),
            date(2025, 10, 31)  # Reformationstag in DE-NW
        ]

        holidays_map = {
            (date(2025, 10, 31), "DE-NW"): True,  # Reformationstag nur in DE-NW
        }

        holidays_by_region = service._calculate_holidays_by_region(
            roster_entries, holidays_map, sprint_days
        )

        # Erwartung: Nur DE-NW hat 1 Feiertag
        assert len(holidays_by_region) == 1
        assert holidays_by_region[0]["region"] == "DE-NW"
        assert holidays_by_region[0]["count"] == 1

    def test_calculate_total_capacity_hours(self, db_session, sample_members):
        """Test: Gesamtkapazität in Stunden"""
        service = AvailabilityService(db_session)

        # Mock roster entries
        alice = next(m for m in sample_members if m.employment_ratio == 1.0)  # 100%
        carol = next(m for m in sample_members if m.employment_ratio == 0.5)  # 50%

        class MockRosterEntry:
            def __init__(self, member, allocation):
                self.member = member
                self.allocation = allocation

        roster_entries = [
            MockRosterEntry(alice, 1.0),    # 100% allocation
            MockRosterEntry(carol, 0.8),    # 80% allocation
        ]

        working_days = 10

        total_hours = service._calculate_total_capacity_hours(roster_entries, working_days)

        # Alice: 10 * 8 * 1.0 * 1.0 = 80 Stunden
        # Carol: 10 * 8 * 0.5 * 0.8 = 32 Stunden
        # Total: 112 Stunden
        expected_hours = 80.0 + 32.0
        assert total_hours == expected_hours

    def test_calculate_total_capacity_days(self, db_session, sample_members):
        """Test: Gesamtkapazität in Tagen"""
        service = AvailabilityService(db_session)

        alice = next(m for m in sample_members if m.employment_ratio == 1.0)  # 100%
        carol = next(m for m in sample_members if m.employment_ratio == 0.5)  # 50%

        class MockRosterEntry:
            def __init__(self, member, allocation):
                self.member = member
                self.allocation = allocation

        roster_entries = [
            MockRosterEntry(alice, 1.0),    # 100% allocation
            MockRosterEntry(carol, 0.6),    # 60% allocation
        ]

        working_days = 10

        total_days = service._calculate_total_capacity_days(roster_entries, working_days)

        # Alice: 10 * 1.0 * 1.0 = 10 Tage
        # Carol: 10 * 0.5 * 0.6 = 3 Tage
        # Total: 13 Tage
        expected_days = 10.0 + 3.0
        assert total_days == expected_days

    def test_calculate_available_capacity_hours(self, db_session):
        """Test: Verfügbare Kapazität in Stunden aus Member-Daten"""
        service = AvailabilityService(db_session)

        # Mock member data
        class MockMember:
            def __init__(self, sum_hours):
                self.sum_hours = sum_hours

        members_data = [
            MockMember(40.0),  # Alice: 40 Stunden
            MockMember(20.0),  # Carol: 20 Stunden
            MockMember(35.0),  # Bogdan: 35 Stunden
        ]

        available_hours = service._calculate_available_capacity_hours(members_data)

        expected_hours = 40.0 + 20.0 + 35.0  # 95.0
        assert available_hours == expected_hours

    def test_calculate_available_capacity_days(self, db_session):
        """Test: Verfügbare Kapazität in Tagen aus Member-Daten"""
        service = AvailabilityService(db_session)

        class MockMember:
            def __init__(self, sum_days):
                self.sum_days = sum_days

        members_data = [
            MockMember(8.0),   # Alice: 8 Tage
            MockMember(3.5),   # Carol: 3.5 Tage
            MockMember(7.2),   # Bogdan: 7.2 Tage
        ]

        available_days = service._calculate_available_capacity_days(members_data)

        expected_days = 8.0 + 3.5 + 7.2  # 18.7
        assert available_days == expected_days

    def test_calculate_efficiency_normal_cases(self, db_session):
        """Test: Effizienzberechnung für normale Fälle"""
        service = AvailabilityService(db_session)

        # Test 1: 100% Effizienz
        efficiency = service._calculate_efficiency(80.0, 80.0)
        assert efficiency == 100

        # Test 2: 75% Effizienz
        efficiency = service._calculate_efficiency(60.0, 80.0)
        assert efficiency == 75

        # Test 3: 120% Effizienz (Überstunden)
        efficiency = service._calculate_efficiency(96.0, 80.0)
        assert efficiency == 120

    def test_calculate_efficiency_edge_cases(self, db_session):
        """Test: Effizienzberechnung für Edge Cases"""
        service = AvailabilityService(db_session)

        # Test 1: Null total_hours (Division durch 0)
        efficiency = service._calculate_efficiency(40.0, 0.0)
        assert efficiency == 0

        # Test 2: Null available_hours
        efficiency = service._calculate_efficiency(0.0, 80.0)
        assert efficiency == 0

        # Test 3: Beide null
        efficiency = service._calculate_efficiency(0.0, 0.0)
        assert efficiency == 0

    def test_calculate_efficiency_rounding(self, db_session):
        """Test: Effizienzberechnung mit Rundung"""
        service = AvailabilityService(db_session)

        # Test mit Nachkommastellen
        efficiency = service._calculate_efficiency(33.33, 80.0)
        # 33.33 / 80.0 = 0.416625 = 41.6625% → rundet zu 42%
        expected = round((33.33 / 80.0) * 100)
        assert efficiency == expected

    def test_calculate_working_days_boundary_conditions(self, db_session):
        """Test: Arbeitstagberechnung für Randbedingungen"""
        service = AvailabilityService(db_session)

        # Test 1: Start = End (gleicher Tag)
        same_day = date(2025, 10, 27)  # Montag
        working_days = service._calculate_working_days(same_day, same_day)
        assert working_days == 1

        # Test 2: Nur Wochenende (Sa-So)
        saturday = date(2025, 11, 1)   # Samstag
        sunday = date(2025, 11, 2)     # Sonntag
        working_days = service._calculate_working_days(saturday, sunday)
        assert working_days == 0

        # Test 3: Ein ganzer Monat
        month_start = date(2025, 10, 1)  # 1. Oktober 2025
        month_end = date(2025, 10, 31)   # 31. Oktober 2025
        working_days = service._calculate_working_days(month_start, month_end)
        # Oktober 2025 hat 23 Werktage (ohne Wochenenden)
        assert working_days == 23

    def test_holidays_calculation_empty_regions(self, db_session):
        """Test: Feiertagsberechnung mit leeren/null Regionen"""
        service = AvailabilityService(db_session)

        # Member ohne region_code
        class MockMember:
            def __init__(self, region_code):
                self.region_code = region_code

        class MockRosterEntry:
            def __init__(self, member):
                self.member = member

        roster_entries = [
            MockRosterEntry(MockMember(None)),    # Kein region_code
            MockRosterEntry(MockMember("")),      # Leerer region_code
        ]

        sprint_days = [date(2025, 10, 31)]
        holidays_map = {(date(2025, 10, 31), "DE-NW"): True}

        holidays_by_region = service._calculate_holidays_by_region(
            roster_entries, holidays_map, sprint_days
        )

        # Erwartung: Keine Feiertage, da keine gültigen Regionen
        assert len(holidays_by_region) == 0
