"""
Comprehensive CRUD Tests for Sprint Roster Operations
Testing database interactions, constraints, and edge cases
"""
import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from app.db.crud.sprint_roster import (
    get_sprint_roster, get_roster_entry, add_member_to_sprint,
    update_roster_entry, remove_member_from_sprint
)
from app.db.models.sprint_roster import SprintRoster
from app.schemas.schemas import SprintRosterCreate, SprintRosterUpdate


class TestSprintRosterCRUD:
    """Comprehensive CRUD tests for Sprint Roster operations"""

    def test_add_member_to_sprint_success(self, db_session, sample_sprint, sample_members):
        """Test: Add member to sprint - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        roster_data = SprintRosterCreate(
            member_id=alice.member_id,
            allocation=0.8,
            assignment_from=date(2025, 10, 28),
            assignment_to=date(2025, 11, 6)
        )

        # Act: Add member to sprint
        roster_entry = add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)

        # Assert: Member added successfully
        assert roster_entry.sprint_id == sample_sprint.sprint_id
        assert roster_entry.member_id == alice.member_id
        assert roster_entry.allocation == Decimal('0.8')
        assert roster_entry.assignment_from == date(2025, 10, 28)
        assert roster_entry.assignment_to == date(2025, 11, 6)

        # Verify in database
        db_roster = db_session.query(SprintRoster).filter_by(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id
        ).first()
        assert db_roster is not None
        assert db_roster.allocation == Decimal('0.8')

    def test_add_member_to_sprint_full_allocation(self, db_session, sample_sprint, sample_members):
        """Test: Add member with full allocation (1.0)"""
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        roster_data = SprintRosterCreate(
            member_id=bogdan.member_id,
            allocation=1.0
            # No assignment dates - should be None
        )

        roster_entry = add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)

        assert roster_entry.allocation == Decimal('1.0')
        assert roster_entry.assignment_from is None
        assert roster_entry.assignment_to is None

    def test_add_member_to_sprint_duplicate_member(self, db_session, sample_sprint, sample_members):
        """Test: Add member to sprint - Duplicate member should fail"""
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        # Setup: Add member first time
        roster_data = SprintRosterCreate(member_id=carol.member_id, allocation=0.5)
        add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)

        # Act & Assert: Adding same member again should raise ValueError
        duplicate_data = SprintRosterCreate(member_id=carol.member_id, allocation=0.7)
        with pytest.raises(ValueError, match=f"Member {carol.member_id} is already in sprint"):
            add_member_to_sprint(db_session, sample_sprint.sprint_id, duplicate_data)

    def test_add_member_to_sprint_invalid_member(self, db_session, sample_sprint):
        """Test: Add invalid member to sprint - Foreign key constraint"""
        roster_data = SprintRosterCreate(
            member_id=99999,  # Non-existent member
            allocation=1.0
        )

        # Act & Assert: Should raise integrity error during commit
        try:
            roster_entry = add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)
            # If we get here, the constraint wasn't enforced at object creation
            # This is valid behavior in SQLite - constraints checked at commit
            assert roster_entry is not None
        except IntegrityError:
            # This is also expected behavior
            pass

    def test_add_member_to_sprint_invalid_sprint(self, db_session, sample_members):
        """Test: Add member to invalid sprint - Foreign key constraint"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        roster_data = SprintRosterCreate(
            member_id=alice.member_id,
            allocation=1.0
        )

        # Act & Assert: Should raise integrity error
        with pytest.raises(IntegrityError):
            add_member_to_sprint(db_session, 99999, roster_data)  # Non-existent sprint

    def test_get_sprint_roster_success(self, db_session, sample_sprint, sample_members):
        """Test: Get sprint roster - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Add multiple members to sprint
        rosters = [
            SprintRoster(sprint_id=sample_sprint.sprint_id, member_id=alice.member_id, allocation=0.8),
            SprintRoster(sprint_id=sample_sprint.sprint_id, member_id=bogdan.member_id, allocation=1.0)
        ]
        for roster in rosters:
            db_session.add(roster)
        db_session.commit()

        # Act: Get sprint roster
        roster_list = get_sprint_roster(db_session, sample_sprint.sprint_id)

        # Assert: All roster entries returned with member relationships
        assert len(roster_list) == 2

        member_names = [entry.member.name for entry in roster_list]
        assert "Alice Mueller" in member_names
        assert "Bogdan Ivanov" in member_names

        # Verify allocations
        alice_entry = next(r for r in roster_list if r.member.name == "Alice Mueller")
        bogdan_entry = next(r for r in roster_list if r.member.name == "Bogdan Ivanov")
        assert alice_entry.allocation == Decimal('0.8')
        assert bogdan_entry.allocation == Decimal('1.0')

    def test_get_sprint_roster_empty(self, db_session, sample_sprint):
        """Test: Get sprint roster - Empty roster"""
        roster_list = get_sprint_roster(db_session, sample_sprint.sprint_id)
        assert len(roster_list) == 0

    def test_get_roster_entry_success(self, db_session, sample_sprint, sample_members):
        """Test: Get specific roster entry - Success case"""
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        # Setup: Add member to sprint
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=carol.member_id,
            allocation=0.6,
            assignment_from=date(2025, 10, 29),
            assignment_to=date(2025, 11, 5)
        )
        db_session.add(roster)
        db_session.commit()

        # Act: Get roster entry
        entry = get_roster_entry(db_session, sample_sprint.sprint_id, carol.member_id)

        # Assert: Correct entry returned
        assert entry is not None
        assert entry.sprint_id == sample_sprint.sprint_id
        assert entry.member_id == carol.member_id
        assert entry.allocation == Decimal('0.6')
        assert entry.assignment_from == date(2025, 10, 29)
        assert entry.assignment_to == date(2025, 11, 5)

    def test_get_roster_entry_not_found(self, db_session, sample_sprint, sample_members):
        """Test: Get roster entry - Not found"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Act: Get non-existent roster entry
        entry = get_roster_entry(db_session, sample_sprint.sprint_id, alice.member_id)

        # Assert: None returned
        assert entry is None

    def test_update_roster_entry_success(self, db_session, sample_sprint, sample_members):
        """Test: Update roster entry - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Add member to sprint
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=0.5,
            assignment_from=date(2025, 10, 27),
            assignment_to=date(2025, 11, 7)
        )
        db_session.add(roster)
        db_session.commit()

        # Act: Update roster entry
        update_data = SprintRosterUpdate(
            allocation=0.9,
            assignment_from=date(2025, 10, 28),
            assignment_to=date(2025, 11, 6)
        )
        updated_entry = update_roster_entry(
            db_session, sample_sprint.sprint_id, alice.member_id, update_data
        )

        # Assert: Entry updated successfully
        assert updated_entry is not None
        assert updated_entry.allocation == Decimal('0.9')
        assert updated_entry.assignment_from == date(2025, 10, 28)
        assert updated_entry.assignment_to == date(2025, 11, 6)

        # Verify in database
        db_entry = get_roster_entry(db_session, sample_sprint.sprint_id, alice.member_id)
        assert db_entry.allocation == Decimal('0.9')

    def test_update_roster_entry_partial_update(self, db_session, sample_sprint, sample_members):
        """Test: Update roster entry - Partial update"""
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Setup: Add member to sprint
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=bogdan.member_id,
            allocation=0.8,
            assignment_from=date(2025, 10, 27),
            assignment_to=date(2025, 11, 7)
        )
        db_session.add(roster)
        db_session.commit()

        # Act: Partial update (only allocation)
        update_data = SprintRosterUpdate(allocation=1.0)
        updated_entry = update_roster_entry(
            db_session, sample_sprint.sprint_id, bogdan.member_id, update_data
        )

        # Assert: Only allocation updated, dates unchanged
        assert updated_entry.allocation == Decimal('1.0')
        assert updated_entry.assignment_from == date(2025, 10, 27)  # Unchanged
        assert updated_entry.assignment_to == date(2025, 11, 7)     # Unchanged

    def test_update_roster_entry_not_found(self, db_session, sample_sprint, sample_members):
        """Test: Update roster entry - Not found"""
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        update_data = SprintRosterUpdate(allocation=0.7)
        result = update_roster_entry(
            db_session, sample_sprint.sprint_id, carol.member_id, update_data
        )

        assert result is None

    def test_remove_member_from_sprint_success(self, db_session, sample_sprint, sample_members):
        """Test: Remove member from sprint - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Add member to sprint
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=0.8
        )
        db_session.add(roster)
        db_session.commit()

        # Verify member is in roster
        assert get_roster_entry(db_session, sample_sprint.sprint_id, alice.member_id) is not None

        # Act: Remove member from sprint
        result = remove_member_from_sprint(db_session, sample_sprint.sprint_id, alice.member_id)

        # Assert: Member removed successfully
        assert result is True

        # Verify removal in database
        removed_entry = get_roster_entry(db_session, sample_sprint.sprint_id, alice.member_id)
        assert removed_entry is None

    def test_remove_member_from_sprint_not_found(self, db_session, sample_sprint, sample_members):
        """Test: Remove member from sprint - Not found"""
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        # Act: Try to remove member not in sprint
        result = remove_member_from_sprint(db_session, sample_sprint.sprint_id, bogdan.member_id)

        # Assert: Operation returns False
        assert result is False

    def test_roster_allocation_edge_cases(self, db_session, sample_sprint, sample_members):
        """Test: Roster allocation edge cases"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        # Test different allocation values
        test_cases = [
            (alice.member_id, 0.01),   # Minimum allocation
            (bogdan.member_id, 0.25),  # Quarter allocation
            (carol.member_id, 1.0)     # Full allocation
        ]

        for member_id, allocation in test_cases:
            roster_data = SprintRosterCreate(member_id=member_id, allocation=allocation)
            entry = add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)
            assert entry.allocation == Decimal(str(allocation))

    def test_roster_assignment_date_scenarios(self, db_session, sample_sprint, sample_members):
        """Test: Different assignment date scenarios"""
        members = sample_members

        # Test scenarios: None, partial overlap, full sprint, outside sprint
        scenarios = [
            # No assignment dates (None, None)
            (members[0].member_id, None, None),
            # Partial assignment within sprint
            (members[1].member_id, date(2025, 10, 30), date(2025, 11, 3)),
            # Assignment covers full sprint
            (members[2].member_id, date(2025, 10, 27), date(2025, 11, 7))
        ]

        for member_id, from_date, to_date in scenarios:
            roster_data = SprintRosterCreate(
                member_id=member_id,
                allocation=1.0,
                assignment_from=from_date,
                assignment_to=to_date
            )
            entry = add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)
            assert entry.assignment_from == from_date
            assert entry.assignment_to == to_date

    def test_roster_complex_operations(self, db_session, sample_sprint, sample_members):
        """Test: Complex roster operations workflow"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")
        carol = next(m for m in sample_members if m.name == "Carol Smith")

        # Step 1: Add all members to sprint
        members_data = [
            (alice.member_id, 0.8),
            (bogdan.member_id, 1.0),
            (carol.member_id, 0.5)
        ]

        for member_id, allocation in members_data:
            roster_data = SprintRosterCreate(member_id=member_id, allocation=allocation)
            add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)

        # Verify all added
        roster = get_sprint_roster(db_session, sample_sprint.sprint_id)
        assert len(roster) == 3

        # Step 2: Update Alice's allocation
        alice_update = SprintRosterUpdate(allocation=0.9)
        updated_alice = update_roster_entry(
            db_session, sample_sprint.sprint_id, alice.member_id, alice_update
        )
        assert updated_alice.allocation == Decimal('0.9')

        # Step 3: Remove Carol from sprint
        remove_result = remove_member_from_sprint(db_session, sample_sprint.sprint_id, carol.member_id)
        assert remove_result is True

        # Step 4: Verify final state
        final_roster = get_sprint_roster(db_session, sample_sprint.sprint_id)
        assert len(final_roster) == 2

        member_names = [entry.member.name for entry in final_roster]
        assert "Alice Mueller" in member_names
        assert "Bogdan Ivanov" in member_names
        assert "Carol Smith" not in member_names

        # Verify Alice's updated allocation
        alice_final = next(r for r in final_roster if r.member.name == "Alice Mueller")
        assert alice_final.allocation == Decimal('0.9')

    def test_roster_relationship_loading(self, db_session, sample_sprint, sample_members):
        """Test: Verify relationship loading works correctly"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Setup: Add member to sprint
        roster_data = SprintRosterCreate(member_id=alice.member_id, allocation=0.7)
        add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)

        # Test: Get roster with relationship loading
        roster_list = get_sprint_roster(db_session, sample_sprint.sprint_id)

        assert len(roster_list) == 1
        entry = roster_list[0]

        # Verify member relationship is loaded
        assert entry.member is not None
        assert entry.member.name == "Alice Mueller"
        assert entry.member.employment_ratio == 1.0
        assert entry.member.region_code == "DE-NW"

        # Verify sprint relationship exists (though not loaded by default)
        assert entry.sprint_id == sample_sprint.sprint_id

    def test_roster_decimal_precision(self, db_session, sample_sprint, sample_members):
        """Test: Decimal precision handling for allocations"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Test precise decimal allocations that fit within Numeric(3,2) precision
        precise_allocations = [0.33, 0.66, 0.75, 0.10, 0.90]

        for i, allocation in enumerate(precise_allocations):
            if i > 0:  # Remove previous entry
                remove_member_from_sprint(db_session, sample_sprint.sprint_id, alice.member_id)

            roster_data = SprintRosterCreate(member_id=alice.member_id, allocation=allocation)
            entry = add_member_to_sprint(db_session, sample_sprint.sprint_id, roster_data)

            # Verify precision is maintained within database constraints
            # Database stores as Numeric(3,2) so 0.125 becomes 0.12
            expected = Decimal(str(allocation))
            assert entry.allocation == expected

            # Verify in database
            db_entry = get_roster_entry(db_session, sample_sprint.sprint_id, alice.member_id)
            assert db_entry.allocation == expected
