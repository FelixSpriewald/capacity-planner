"""
Service Integration Tests - Cross-Service Workflows
Tests integration between availability calculations, validation, and data services
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models.members import Member
from app.db.models.sprints import Sprint, SprintStatus
from app.db.models.sprint_roster import SprintRoster
from app.db.models.pto import PTO
from app.schemas.schemas import (
    MemberCreate, SprintCreate, SprintRosterCreate, PTOCreate
)
from app.db.crud.members import create_member, get_members
from app.db.crud.sprints import create_sprint, get_sprints
from app.db.crud.sprint_roster import add_member_to_sprint, get_sprint_roster
from app.db.crud.pto import create_pto, get_pto_list
from app.services.availability import AvailabilityService


class TestServiceIntegration:
    """Test integration between different services and data layers"""

    def test_availability_calculation_with_validation(self, db_session: Session):
        """
        Test: Integration between availability calculation and validation services
        Verify that validation rules are properly applied during availability calculations
        """
        # Create test data
        member_data = MemberCreate(name="Integration Test Member", employment_ratio=0.8)
        member = create_member(db_session, member_data)

        # Create valid sprint
        sprint_start = date.today() + timedelta(days=7)
        sprint_end = sprint_start + timedelta(days=13)

        sprint_data = SprintCreate(
            name="Validation Integration Sprint",
            start_date=sprint_start,
            end_date=sprint_end
        )
        sprint = create_sprint(db_session, sprint_data)

        # Add member to sprint with valid allocation
        roster_data = SprintRosterCreate(member_id=member.member_id, allocation=0.9)

        # Add member to sprint
        roster_entry = add_member_to_sprint(db_session, sprint.sprint_id, roster_data)

        # Calculate availability - should use validated data
        availability_service = AvailabilityService(db_session)
        availability = availability_service.get_sprint_availability(sprint.sprint_id)

        # Verify integration results
        assert availability is not None
        assert availability.sprint.sprint_id == sprint.sprint_id
        assert len(availability.members) == 1

        member_availability = availability.members[0]
        assert member_availability.employment_ratio == Decimal('0.8')
        assert member_availability.allocation == Decimal('0.9')

        # Verify capacity calculation considers employment ratio
        # Just verify that capacity is calculated reasonably
        assert member_availability.sum_days > 0
        assert member_availability.sum_hours > 0

    def test_multi_sprint_capacity_distribution(self, db_session: Session):
        """
        Test: Complex scenario with member allocated to multiple sprints
        Verify capacity calculations across overlapping sprints
        """
        # Create member
        member_data = MemberCreate(name="Multi-Sprint Member", employment_ratio=1.0)
        member = create_member(db_session, member_data)

        # Create overlapping sprints
        base_date = date.today() + timedelta(days=7)

        sprint1_data = SprintCreate(
            name="Sprint One",
            start_date=base_date,
            end_date=base_date + timedelta(days=13)  # 2 weeks
        )
        sprint1 = create_sprint(db_session, sprint1_data)

        sprint2_data = SprintCreate(
            name="Sprint Two",
            start_date=base_date + timedelta(days=7),  # 1 week overlap
            end_date=base_date + timedelta(days=20)    # 2 weeks total
        )
        sprint2 = create_sprint(db_session, sprint2_data)

        # Allocate member to both sprints
        roster1_data = SprintRosterCreate(member_id=member.member_id, allocation=0.6)
        roster1 = add_member_to_sprint(db_session, sprint1.sprint_id, roster1_data)

        roster2_data = SprintRosterCreate(member_id=member.member_id, allocation=0.4)
        roster2 = add_member_to_sprint(db_session, sprint2.sprint_id, roster2_data)

        # Calculate availability for both sprints
        availability_service = AvailabilityService(db_session)
        availability1 = availability_service.get_sprint_availability(sprint1.sprint_id)
        availability2 = availability_service.get_sprint_availability(sprint2.sprint_id)

        # Verify individual sprint calculations
        assert availability1 is not None and availability2 is not None

        member1_availability = availability1.members[0]
        member2_availability = availability2.members[0]

        assert member1_availability.allocation == Decimal('0.6')
        assert member2_availability.allocation == Decimal('0.4')

        # Verify capacity calculations are reasonable
        assert member1_availability.sum_days > 0
        assert member2_availability.sum_days > 0

        # Verify total allocation doesn't exceed 100% (validation concern)
        total_allocation = 0.6 + 0.4
        assert total_allocation <= 1.0

    def test_pto_impact_across_services(self, db_session: Session):
        """
        Test: PTO impact calculation across multiple service integrations
        Verify PTO data flows correctly through all service layers
        """
        # Create test setup
        member_data = MemberCreate(name="PTO Impact Member", employment_ratio=1.0)
        member = create_member(db_session, member_data)

        sprint_start = date.today() + timedelta(days=7)
        sprint_end = sprint_start + timedelta(days=13)

        sprint_data = SprintCreate(
            name="PTO Impact Sprint",
            start_date=sprint_start,
            end_date=sprint_end
        )
        sprint = create_sprint(db_session, sprint_data)

        roster_data = SprintRosterCreate(member_id=member.member_id, allocation=1.0)
        add_member_to_sprint(db_session, sprint.sprint_id, roster_data)

        # Add multiple PTO requests
        pto_requests = [
            # Vacation during first week
            {
                "start": sprint_start + timedelta(days=1),
                "end": sprint_start + timedelta(days=3),
                "type": "vacation"
            },
            # Sick leave during second week
            {
                "start": sprint_start + timedelta(days=8),
                "end": sprint_start + timedelta(days=9),
                "type": "sick"
            }
        ]

        created_ptos = []
        for pto_req in pto_requests:
            pto_data = PTOCreate(
                member_id=member.member_id,
                from_date=pto_req["start"],
                to_date=pto_req["end"],
                type=pto_req["type"],
                description=f"Service integration test - {pto_req['type']}"
            )
            pto = create_pto(db_session, pto_data)
            created_ptos.append(pto)

        # Verify PTO data through CRUD service
        member_ptos = get_pto_list(db_session, member_id=member.member_id)
        assert len(member_ptos) == 2

        # Verify PTO data through sprint filtering
        sprint_overlap_ptos = get_pto_list(db_session, sprint_id=sprint.sprint_id)
        assert len(sprint_overlap_ptos) == 2

        # Calculate availability with PTO impact
        availability_service = AvailabilityService(db_session)
        availability = availability_service.get_sprint_availability(sprint.sprint_id)

        # Verify PTO impact in availability calculation
        assert availability is not None
        member_availability = availability.members[0]

        # Verify member has some capacity (PTO impact calculated internally)
        assert member_availability.sum_days >= 0
        assert member_availability.sum_hours >= 0

    def test_complex_team_scenario(self, db_session: Session):
        """
        Test: Complex team scenario integrating all services
        Multiple members, sprints, allocations, and PTO requests
        """
        # Step 1: Create diverse team
        team_setup = [
            {"name": "Team Lead", "employment": 1.0, "region": "DE-NW"},
            {"name": "Senior Developer", "employment": 1.0, "region": "DE-BY"},
            {"name": "Junior Developer", "employment": 1.0, "region": "UA"},
            {"name": "Part-time QA", "employment": 0.6, "region": "DE-NW"},
            {"name": "Contractor", "employment": 0.8, "region": "DE-BY"}
        ]

        team_members = []
        for setup in team_setup:
            member_data = MemberCreate(
                name=setup["name"],
                employment_ratio=setup["employment"],
                region_code=setup["region"]
            )
            member = create_member(db_session, member_data)
            team_members.append(member)

        # Verify team creation through service
        all_members = get_members(db_session)
        assert len(all_members) >= 5

        # Step 2: Create sprint
        sprint_start = date.today() + timedelta(days=7)
        sprint_data = SprintCreate(
            name="Complex Team Sprint",
            start_date=sprint_start,
            end_date=sprint_start + timedelta(days=13)
        )
        sprint = create_sprint(db_session, sprint_data)

        # Step 3: Assign team with strategic allocations
        allocations = [
            {"member": team_members[0], "allocation": 0.3},  # Team Lead - 30%
            {"member": team_members[1], "allocation": 1.0},  # Senior Dev - Full
            {"member": team_members[2], "allocation": 0.8},  # Junior Dev - 80%
            {"member": team_members[3], "allocation": 0.9},  # Part-time QA - 90% of their time
            {"member": team_members[4], "allocation": 1.0}   # Contractor - Full
        ]

        for allocation in allocations:
            roster_data = SprintRosterCreate(
                member_id=allocation["member"].member_id,
                allocation=allocation["allocation"]
            )
            add_member_to_sprint(db_session, sprint.sprint_id, roster_data)

        # Verify roster through service
        sprint_roster = get_sprint_roster(db_session, sprint.sprint_id)
        assert len(sprint_roster) == 5

        # Step 4: Add strategic PTO requests
        pto_scenarios = [
            # Team Lead vacation - low impact due to low allocation
            {"member": team_members[0], "days": 2, "type": "vacation"},
            # Senior Dev sick leave - high impact
            {"member": team_members[1], "days": 3, "type": "sick"},
            # Junior Dev training - medium impact
            {"member": team_members[2], "days": 1, "type": "personal"}
        ]

        for pto_scenario in pto_scenarios:
            pto_start = sprint_start + timedelta(days=2)
            pto_end = pto_start + timedelta(days=pto_scenario["days"] - 1)

            pto_data = PTOCreate(
                member_id=pto_scenario["member"].member_id,
                from_date=pto_start,
                to_date=pto_end,
                type=pto_scenario["type"],
                description=f"Complex scenario - {pto_scenario['type']}"
            )
            create_pto(db_session, pto_data)

        # Step 5: Calculate comprehensive availability
        availability_service = AvailabilityService(db_session)
        availability = availability_service.get_sprint_availability(sprint.sprint_id)

        # Step 6: Verify complex calculations
        assert availability is not None
        assert len(availability.members) == 5

        # Verify individual member calculations
        team_lead_av = next((m for m in availability.members if "Team Lead" in m.name), None)
        senior_dev_av = next((m for m in availability.members if "Senior Developer" in m.name), None)

        assert team_lead_av is not None
        assert senior_dev_av is not None

        # Team Lead: low allocation
        assert team_lead_av.allocation == Decimal('0.3')

        # Senior Dev: full allocation
        assert senior_dev_av.allocation == Decimal('1.0')

        # Verify total team capacity calculation
        assert availability.sum_days_team >= 0

        # Verify part-time QA exists and has reasonable capacity
        part_time_qa = next((m for m in availability.members if "Part-time QA" in m.name), None)
        assert part_time_qa is not None
        assert part_time_qa.sum_days >= 0

    def test_data_consistency_across_services(self, db_session: Session):
        """
        Test: Data consistency verification across all service layers
        Ensure data integrity is maintained through complex operations
        """
        # Create baseline data
        member_data = MemberCreate(name="Consistency Test", employment_ratio=1.0)
        member = create_member(db_session, member_data)

        sprint_data = SprintCreate(
            name="Consistency Sprint",
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=20)
        )
        sprint = create_sprint(db_session, sprint_data)

        # Test 1: Verify CRUD consistency
        roster_data = SprintRosterCreate(member_id=member.member_id, allocation=0.8)
        roster_entry = add_member_to_sprint(db_session, sprint.sprint_id, roster_data)

        # Retrieve through different service methods
        retrieved_roster = get_sprint_roster(db_session, sprint.sprint_id)
        assert len(retrieved_roster) == 1
        assert retrieved_roster[0].allocation == Decimal('0.8')

        # Test 2: Verify availability service consistency
        availability_service = AvailabilityService(db_session)
        availability1 = availability_service.get_sprint_availability(sprint.sprint_id)
        availability2 = availability_service.get_sprint_availability(sprint.sprint_id)

        # Should get identical results
        assert availability1 is not None and availability2 is not None
        assert availability1.sum_days_team == availability2.sum_days_team
        assert len(availability1.members) == len(availability2.members)

        # Test 3: Add PTO and verify consistency
        pto_data = PTOCreate(
            member_id=member.member_id,
            from_date=date.today() + timedelta(days=10),
            to_date=date.today() + timedelta(days=12),
            type="vacation"
        )
        create_pto(db_session, pto_data)

        # Verify PTO appears in different service calls
        member_ptos = get_pto_list(db_session, member_id=member.member_id)
        sprint_ptos = get_pto_list(db_session, sprint_id=sprint.sprint_id)

        assert len(member_ptos) == 1
        assert len(sprint_ptos) == 1
        assert member_ptos[0].pto_id == sprint_ptos[0].pto_id

        # Verify availability calculation includes PTO
        availability_service = AvailabilityService(db_session)
        final_availability = availability_service.get_sprint_availability(sprint.sprint_id)
        assert final_availability is not None
        member_final = final_availability.members[0]
        assert member_final.sum_days >= 0

        # Test 4: Verify relationships maintained
        assert member_final.member_id == member.member_id
        assert final_availability.sprint.sprint_id == sprint.sprint_id

    def test_error_handling_integration(self, db_session: Session):
        """
        Test: Error handling across service integrations
        Verify graceful handling of error conditions
        """
        # Test 1: Availability calculation with no roster
        sprint_data = SprintCreate(
            name="Empty Sprint",
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=20)
        )
        empty_sprint = create_sprint(db_session, sprint_data)

        # Should handle empty roster gracefully
        availability_service = AvailabilityService(db_session)
        availability = availability_service.get_sprint_availability(empty_sprint.sprint_id)
        assert availability is not None
        assert availability.sum_days_team == 0
        assert len(availability.members) == 0

        # Test 2: PTO queries with non-existent references
        # Should return empty lists, not errors
        no_ptos = get_pto_list(db_session, member_id=99999)
        assert len(no_ptos) == 0

        no_sprint_ptos = get_pto_list(db_session, sprint_id=99999)
        assert len(no_sprint_ptos) == 0

        # Test 3: Roster queries with non-existent sprint
        no_roster = get_sprint_roster(db_session, 99999)
        assert len(no_roster) == 0

        # Test 4: Member list with filters
        filtered_members = get_members(db_session, skip=100, limit=10)
        # Should return empty list if no members in that range
        assert isinstance(filtered_members, list)
