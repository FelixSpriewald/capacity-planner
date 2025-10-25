"""
Simplified CRUD Tests for PTO Operations - Fixed Schema Issues
"""
import pytest
from datetime import date
from app.db.crud.pto import (
    get_pto_list, get_pto, create_pto, update_pto, delete_pto
)
from app.db.models.pto import PTO
from app.schemas.schemas import PTOCreate


class TestPTOCRUDFixed:
    """Fixed PTO CRUD tests that work with actual schemas"""

    def test_create_pto_success(self, db_session, sample_members):
        """Test: Create new PTO entry - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        pto_data = PTOCreate(
            member_id=alice.member_id,
            from_date=date(2025, 12, 20),
            to_date=date(2025, 12, 31),
            description="Christmas holidays"
        )

        # Act: Create PTO
        created_pto = create_pto(db_session, pto_data)

        # Assert: PTO created successfully
        assert created_pto.pto_id is not None
        assert created_pto.member_id == alice.member_id
        assert created_pto.from_date == date(2025, 12, 20)
        assert created_pto.to_date == date(2025, 12, 31)
        assert created_pto.notes == "Christmas holidays"  # Schema maps description to notes

    def test_get_pto_by_id_success(self, db_session, sample_members):
        """Test: Get PTO by ID - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Create PTO directly with model
        pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 10),
            to_date=date(2025, 11, 12),
            notes="Flu symptoms"
        )
        db_session.add(pto)
        db_session.commit()

        # Act: Get PTO
        retrieved_pto = get_pto(db_session, pto.pto_id)

        # Assert: PTO retrieved with member relationship loaded
        assert retrieved_pto is not None
        assert retrieved_pto.pto_id == pto.pto_id
        assert retrieved_pto.member_id == alice.member_id
        assert retrieved_pto.notes == "Flu symptoms"

        # Verify relationship is loaded
        assert retrieved_pto.member is not None
        assert retrieved_pto.member.name == "Alice Mueller"

    def test_get_pto_list_all(self, db_session, sample_members):
        """Test: Get all PTO entries"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Create multiple PTO entries
        ptos = [
            PTO(member_id=alice.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 3), notes="vacation"),
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 10), to_date=date(2025, 11, 11), notes="sick"),
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 15), to_date=date(2025, 12, 20), notes="personal")
        ]
        for pto in ptos:
            db_session.add(pto)
        db_session.commit()

        # Act: Get all PTOs
        all_ptos = get_pto_list(db_session)

        # Assert: All PTOs retrieved
        assert len(all_ptos) == 3
        # Verify member relationships are loaded
        for pto in all_ptos:
            assert pto.member is not None
            assert pto.member.name in ["Alice Mueller", "Bogdan Ivanov"]

    def test_get_pto_list_by_member(self, db_session, sample_members):
        """Test: Get PTO entries filtered by member"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Create PTOs for different members
        ptos = [
            PTO(member_id=alice.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 3), notes="vacation"),
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 10), to_date=date(2025, 11, 11), notes="sick"),
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 15), to_date=date(2025, 12, 20), notes="personal")
        ]
        for pto in ptos:
            db_session.add(pto)
        db_session.commit()

        # Act: Get PTOs for Alice only
        alice_ptos = get_pto_list(db_session, member_id=alice.member_id)

        # Assert: Only Alice's PTOs returned
        assert len(alice_ptos) == 2
        for pto in alice_ptos:
            assert pto.member_id == alice.member_id
            assert pto.member.name == "Alice Mueller"

    def test_get_pto_list_by_sprint_overlap(self, db_session, sample_members, sample_sprint):
        """Test: Get PTO entries that overlap with a sprint"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Sprint runs from 2025-10-27 to 2025-11-07
        # Setup: Create PTOs with different overlap scenarios
        ptos = [
            # Overlaps start of sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 10, 25), to_date=date(2025, 10, 30), notes="vacation"),
            # Completely within sprint
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 3), notes="sick"),
            # Overlaps end of sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 11, 5), to_date=date(2025, 11, 10), notes="personal"),
            # No overlap - before sprint
            PTO(member_id=bogdan.member_id, from_date=date(2025, 9, 1), to_date=date(2025, 9, 5), notes="vacation"),
            # No overlap - after sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 1), to_date=date(2025, 12, 5), notes="vacation")
        ]
        for pto in ptos:
            db_session.add(pto)
        db_session.commit()

        # Act: Get PTOs that overlap with sprint
        overlapping_ptos = get_pto_list(db_session, sprint_id=sample_sprint.sprint_id)

        # Assert: Only overlapping PTOs returned (first 3)
        assert len(overlapping_ptos) == 3
        overlap_dates = [(pto.from_date, pto.to_date) for pto in overlapping_ptos]
        expected_dates = [
            (date(2025, 10, 25), date(2025, 10, 30)),  # Overlaps start
            (date(2025, 11, 1), date(2025, 11, 3)),    # Within sprint
            (date(2025, 11, 5), date(2025, 11, 10))    # Overlaps end
        ]
        for expected in expected_dates:
            assert expected in overlap_dates

    def test_update_pto_success(self, db_session, sample_members):
        """Test: Update PTO entry - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Create PTO
        pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 10),
            to_date=date(2025, 11, 12),
            notes="Initial notes"
        )
        db_session.add(pto)
        db_session.commit()

        # Act: Update PTO
        update_data = {
            "to_date": date(2025, 11, 15),  # Extend vacation
            "notes": "Updated notes"
        }
        updated_pto = update_pto(db_session, pto.pto_id, update_data)

        # Assert: PTO updated successfully
        assert updated_pto is not None
        assert updated_pto.pto_id == pto.pto_id
        assert updated_pto.from_date == date(2025, 11, 10)  # Unchanged
        assert updated_pto.to_date == date(2025, 11, 15)    # Updated
        assert updated_pto.notes == "Updated notes"         # Updated

    def test_delete_pto_success(self, db_session, sample_members):
        """Test: Delete PTO entry - Success case"""
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        # Setup: Create PTO
        pto = PTO(
            member_id=carol.member_id,
            from_date=date(2025, 12, 1),
            to_date=date(2025, 12, 3),
            notes="personal time"
        )
        db_session.add(pto)
        db_session.commit()
        pto_id = pto.pto_id

        # Act: Delete PTO
        result = delete_pto(db_session, pto_id)

        # Assert: PTO deleted successfully
        assert result is True

        # Verify deletion in database
        deleted_pto = db_session.get(PTO, pto_id)
        assert deleted_pto is None

    def test_delete_pto_not_found(self, db_session):
        """Test: Delete PTO entry - Not found"""
        result = delete_pto(db_session, 99999)
        assert result is False

    def test_get_pto_by_id_not_found(self, db_session):
        """Test: Get PTO by ID - Not found"""
        result = get_pto(db_session, 99999)
        assert result is None
