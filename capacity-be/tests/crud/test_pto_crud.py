"""
Comprehensive CRUD Tests for PTO (Personal Time Off) Operations
Testing database interactions, constraints, and edge cases
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from app.db.crud.pto import (
    get_pto_list, get_pto, create_pto, update_pto, delete_pto
)
from app.db.models.pto import PTO
from app.schemas.schemas import PTOCreate


class TestPTOCRUD:
    """Comprehensive CRUD tests for PTO operations"""

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
        assert created_pto.notes == "Christmas holidays"

        # Verify in database
        db_pto = db_session.get(PTO, created_pto.pto_id)
        assert db_pto is not None
        assert db_pto.member_id == alice.member_id

    def test_create_pto_invalid_member_id(self, db_session):
        """Test: Create PTO with invalid member_id - Foreign key constraint"""
        pto_data = PTOCreate(
            member_id=99999,  # Non-existent member
            from_date=date(2025, 12, 20),
            to_date=date(2025, 12, 31)
        )

        # Act & Assert: Should raise integrity error
        with pytest.raises(IntegrityError):
            create_pto(db_session, pto_data)

    def test_create_pto_default_type(self, db_session, sample_members):
        """Test: Create PTO with default type"""
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        pto_data = PTOCreate(
            member_id=bogdan.member_id,
            from_date=date(2025, 11, 15),
            to_date=date(2025, 11, 16)
        )

        created_pto = create_pto(db_session, pto_data)

        assert created_pto.notes is None  # Optional field

    def test_get_pto_by_id_success(self, db_session, sample_members):
        """Test: Get PTO by ID - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Create PTO
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

    def test_get_pto_by_id_not_found(self, db_session):
        """Test: Get PTO by ID - Not found"""
        result = get_pto(db_session, 99999)
        assert result is None

    def test_get_pto_list_all(self, db_session, sample_members):
        """Test: Get all PTO entries"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Create multiple PTO entries
        ptos = [
            PTO(member_id=alice.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 3), type="vacation"),
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 10), to_date=date(2025, 11, 11), type="sick"),
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 15), to_date=date(2025, 12, 20), type="personal")
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
            PTO(member_id=alice.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 3), type="vacation"),
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 10), to_date=date(2025, 11, 11), type="sick"),
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 15), to_date=date(2025, 12, 20), type="personal")
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
        sprint_start = sample_sprint.start_date
        sprint_end = sample_sprint.end_date

        # Setup: Create PTOs with different overlap scenarios
        ptos = [
            # Overlaps start of sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 10, 25), to_date=date(2025, 10, 30), type="vacation"),
            # Completely within sprint
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 3), type="sick"),
            # Overlaps end of sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 11, 5), to_date=date(2025, 11, 10), type="personal"),
            # No overlap - before sprint
            PTO(member_id=bogdan.member_id, from_date=date(2025, 9, 1), to_date=date(2025, 9, 5), type="vacation"),
            # No overlap - after sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 1), to_date=date(2025, 12, 5), type="vacation")
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

    def test_get_pto_list_pagination(self, db_session, sample_members):
        """Test: Get PTO entries with pagination"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Create multiple PTO entries
        ptos = [
            PTO(member_id=alice.member_id, from_date=date(2025, 11, i), to_date=date(2025, 11, i+1), type="vacation")
            for i in range(1, 6)  # Create 5 PTO entries
        ]
        for pto in ptos:
            db_session.add(pto)
        db_session.commit()

        # Act: Test pagination
        page1 = get_pto_list(db_session, skip=0, limit=2)
        page2 = get_pto_list(db_session, skip=2, limit=2)
        page3 = get_pto_list(db_session, skip=4, limit=2)

        # Assert: Pagination works correctly
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1  # Only 1 remaining

        # Verify no duplicates across pages
        all_ids = [pto.pto_id for pto in page1 + page2 + page3]
        assert len(all_ids) == len(set(all_ids))  # No duplicates

    def test_update_pto_success(self, db_session, sample_members):
        """Test: Update PTO entry - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Create PTO
        pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 10),
            to_date=date(2025, 11, 12),
            type="vacation",
            notes="Initial notes"
        )
        db_session.add(pto)
        db_session.commit()

        # Act: Update PTO
        update_data = {
            "to_date": date(2025, 11, 15),  # Extend vacation
            "type": "personal",
            "notes": "Updated notes"
        }
        updated_pto = update_pto(db_session, pto.pto_id, update_data)

        # Assert: PTO updated successfully
        assert updated_pto is not None
        assert updated_pto.pto_id == pto.pto_id
        assert updated_pto.from_date == date(2025, 11, 10)  # Unchanged
        assert updated_pto.to_date == date(2025, 11, 15)    # Updated
        assert updated_pto.type == "personal"               # Updated
        assert updated_pto.notes == "Updated notes"         # Updated

        # Verify in database
        db_pto = db_session.get(PTO, pto.pto_id)
        assert db_pto.to_date == date(2025, 11, 15)
        assert db_pto.type == "personal"

    def test_update_pto_partial_update(self, db_session, sample_members):
        """Test: Update PTO entry - Partial update"""
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Create PTO
        pto = PTO(
            member_id=bogdan.member_id,
            from_date=date(2025, 11, 20),
            to_date=date(2025, 11, 22),
            type="sick",
            notes="Flu"
        )
        db_session.add(pto)
        db_session.commit()

        # Act: Partial update (only notes)
        update_data = {"notes": "Recovery going well"}
        updated_pto = update_pto(db_session, pto.pto_id, update_data)

        # Assert: Only specified field updated
        assert updated_pto.notes == "Recovery going well"
        assert updated_pto.type == "sick"        # Unchanged
        assert updated_pto.from_date == date(2025, 11, 20)  # Unchanged
        assert updated_pto.to_date == date(2025, 11, 22)    # Unchanged

    def test_update_pto_not_found(self, db_session):
        """Test: Update PTO entry - Not found"""
        update_data = {"notes": "Should not work"}
        result = update_pto(db_session, 99999, update_data)
        assert result is None

    def test_update_pto_invalid_field(self, db_session, sample_members):
        """Test: Update PTO entry - Invalid field ignored"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Create PTO
        pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 11, 25),
            to_date=date(2025, 11, 26),
            type="vacation"
        )
        db_session.add(pto)
        db_session.commit()

        # Act: Update with invalid field
        update_data = {
            "invalid_field": "should be ignored",
            "notes": "Valid update"
        }
        updated_pto = update_pto(db_session, pto.pto_id, update_data)

        # Assert: Valid field updated, invalid field ignored
        assert updated_pto.notes == "Valid update"
        assert not hasattr(updated_pto, "invalid_field")

    def test_delete_pto_success(self, db_session, sample_members):
        """Test: Delete PTO entry - Success case"""
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        # Setup: Create PTO
        pto = PTO(
            member_id=carol.member_id,
            from_date=date(2025, 12, 1),
            to_date=date(2025, 12, 3),
            type="personal"
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

    def test_pto_date_validation_edge_cases(self, db_session, sample_members):
        """Test: PTO date edge cases and validation"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Test: Same day PTO (from_date == to_date)
        same_day_pto = PTOCreate(
            member_id=alice.member_id,
            from_date=date(2025, 11, 15),
            to_date=date(2025, 11, 15),  # Same day
            type="personal"
        )
        created_pto = create_pto(db_session, same_day_pto)
        assert created_pto.from_date == created_pto.to_date

        # Test: Weekend PTO (should be allowed)
        weekend_pto = PTOCreate(
            member_id=alice.member_id,
            from_date=date(2025, 11, 22),  # Saturday
            to_date=date(2025, 11, 23),    # Sunday
            type="vacation"
        )
        weekend_created = create_pto(db_session, weekend_pto)
        assert weekend_created.from_date.weekday() == 5  # Saturday
        assert weekend_created.to_date.weekday() == 6    # Sunday

    def test_pto_types_variety(self, db_session, sample_members):
        """Test: Different PTO types are handled correctly"""
        members = sample_members
        pto_types = ["vacation", "sick", "personal", "bereavement", "jury_duty", "maternity"]

        created_ptos = []
        for i, pto_type in enumerate(pto_types):
            member = members[i % len(members)]  # Cycle through members
            pto_data = PTOCreate(
                member_id=member.member_id,
                from_date=date(2025, 12, 1 + i),
                to_date=date(2025, 12, 2 + i),
                type=pto_type,
                notes=f"Testing {pto_type} type"
            )
            created_pto = create_pto(db_session, pto_data)
            created_ptos.append(created_pto)

        # Verify all types created successfully
        assert len(created_ptos) == len(pto_types)
        created_types = [pto.type for pto in created_ptos]
        assert set(created_types) == set(pto_types)

    def test_pto_complex_filtering(self, db_session, sample_members, sample_sprint):
        """Test: Complex filtering scenarios"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Create complex PTO scenario
        ptos = [
            # Alice - overlaps with sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 10, 25), to_date=date(2025, 11, 2), type="vacation"),
            # Alice - no overlap with sprint
            PTO(member_id=alice.member_id, from_date=date(2025, 12, 1), to_date=date(2025, 12, 5), type="personal"),
            # Bogdan - overlaps with sprint
            PTO(member_id=bogdan.member_id, from_date=date(2025, 11, 1), to_date=date(2025, 11, 8), type="sick"),
        ]
        for pto in ptos:
            db_session.add(pto)
        db_session.commit()

        # Test: Alice + Sprint overlap
        alice_sprint_ptos = get_pto_list(db_session, member_id=alice.member_id, sprint_id=sample_sprint.sprint_id)
        assert len(alice_sprint_ptos) == 1
        assert alice_sprint_ptos[0].type == "vacation"

        # Test: All sprint overlaps
        all_sprint_ptos = get_pto_list(db_session, sprint_id=sample_sprint.sprint_id)
        assert len(all_sprint_ptos) == 2  # Alice vacation + Bogdan sick

        # Test: Bogdan only
        bogdan_ptos = get_pto_list(db_session, member_id=bogdan.member_id)
        assert len(bogdan_ptos) == 1
        assert bogdan_ptos[0].type == "sick"
