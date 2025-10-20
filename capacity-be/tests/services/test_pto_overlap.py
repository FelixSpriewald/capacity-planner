"""
Tests für PTO-Überlappungen

Test Case 2: PTO-Überlappung Validierung
"""
import pytest
from datetime import date
from app.services.validation import ValidationService, ValidationError
from app.db.models import Member, PTO, AvailabilityState


class TestPTOOverlap:
    """Test PTO-Überlappungs-Validierung"""
    
    def test_pto_overlap_validation_error(self, db_session, sample_members):
        """Test: PTO-Überlappung wird erkannt und verhindert"""
        # Setup: Existing PTO
        alice = sample_members[0]  # Alice Mueller
        
        existing_pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 5),
            notes="Urlaub"
        )
        db_session.add(existing_pto)
        db_session.commit()
        
        # Test: Validation Service
        validator = ValidationService(db_session)
        
        # Case 1: Vollständige Überlappung
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 11, 2),
                to_date=date(2025, 11, 4)
            )
        
        assert "overlaps with existing PTO" in str(exc_info.value)
        
        # Case 2: Überlappung am Anfang
        with pytest.raises(ValidationError):
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 10, 30),
                to_date=date(2025, 11, 2)
            )
        
        # Case 3: Überlappung am Ende
        with pytest.raises(ValidationError):
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 11, 4),
                to_date=date(2025, 11, 8)
            )
        
        # Case 4: Komplette Umhüllung
        with pytest.raises(ValidationError):
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 10, 30),
                to_date=date(2025, 11, 10)
            )
    
    def test_pto_no_overlap_allowed(self, db_session, sample_members):
        """Test: Keine Überlappung erlaubt PTO-Erstellung"""
        alice = sample_members[0]
        
        # Existing PTO
        existing_pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 5),
            notes="Urlaub"
        )
        db_session.add(existing_pto)
        db_session.commit()
        
        # Test: Validation Service
        validator = ValidationService(db_session)
        
        # Case 1: Komplett vor dem existierenden PTO
        try:
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 10, 25),
                to_date=date(2025, 10, 31)  # Endet vor dem 1.11.
            )
            # Sollte keine Exception werfen
        except ValidationError:
            pytest.fail("Unexpected ValidationError for non-overlapping PTO")
        
        # Case 2: Komplett nach dem existierenden PTO
        try:
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 11, 6),  # Startet nach dem 5.11.
                to_date=date(2025, 11, 10)
            )
            # Sollte keine Exception werfen
        except ValidationError:
            pytest.fail("Unexpected ValidationError for non-overlapping PTO")
    
    def test_pto_different_members_no_conflict(self, db_session, sample_members):
        """Test: PTO verschiedener Member überlappen sich nicht"""
        alice = sample_members[0]
        bogdan = sample_members[1]
        
        # Alice PTO
        alice_pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 5),
            notes="Alice Urlaub"
        )
        db_session.add(alice_pto)
        db_session.commit()
        
        # Test: Bogdan kann zur gleichen Zeit PTO haben
        validator = ValidationService(db_session)
        
        try:
            validator.validate_pto_dates(
                member_id=bogdan.member_id,
                from_date=date(2025, 11, 1),  # Gleiche Daten wie Alice
                to_date=date(2025, 11, 5)
            )
            # Sollte keine Exception werfen
        except ValidationError:
            pytest.fail("Unexpected ValidationError for different member PTO")
    
    def test_pto_update_exclude_self(self, db_session, sample_members):
        """Test: PTO Update excludiert sich selbst von Überlappungsprüfung"""
        alice = sample_members[0]
        
        # Existing PTO
        existing_pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 5),
            notes="Urlaub"
        )
        db_session.add(existing_pto)
        db_session.commit()
        
        # Test: Update des gleichen PTO sollte erlaubt sein
        validator = ValidationService(db_session)
        
        try:
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 11, 1),
                to_date=date(2025, 11, 6),  # Erweitert um einen Tag
                exclude_pto_id=existing_pto.pto_id  # Excludiert sich selbst
            )
            # Sollte keine Exception werfen
        except ValidationError:
            pytest.fail("Unexpected ValidationError when updating existing PTO")
    
    def test_pto_invalid_date_range(self, db_session, sample_members):
        """Test: Ungültige Datumsangaben werden erkannt"""
        alice = sample_members[0]
        validator = ValidationService(db_session)
        
        # to_date < from_date sollte Fehler werfen
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_pto_dates(
                member_id=alice.member_id,
                from_date=date(2025, 11, 5),
                to_date=date(2025, 11, 1)  # Früher als from_date
            )
        
        assert "end date must be >= start date" in str(exc_info.value).lower()