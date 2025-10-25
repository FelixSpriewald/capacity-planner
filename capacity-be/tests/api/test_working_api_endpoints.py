"""
Working API Tests for Coverage Improvement
Focus on tests that work with the current API structure
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Sprint, Member, SprintRoster, AvailabilityOverride, AvailabilityState

client = TestClient(app)
API_BASE = "/api/v1"


class TestWorkingAvailabilityAPI:
    """API tests that actually work and improve coverage"""

    def test_get_sprint_availability_success(self, db_session, sample_sprint, sample_members):
        """Test: GET /sprints/{sprint_id}/availability - Success case"""
        # Setup: Add roster entry
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()

        # Act: API call
        response = client.get(f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability")

        # Assert: Success response with correct structure
        assert response.status_code == 200
        data = response.json()

        # Check main structure
        assert "sprint" in data
        assert "members" in data
        assert "working_days" in data
        assert "holidays_by_region" in data
        assert "available_capacity_hours" in data
        assert "available_capacity_days" in data
        assert "efficiency_percentage" in data

        # Check sprint data
        sprint_data = data["sprint"]
        assert sprint_data["sprint_id"] == sample_sprint.sprint_id
        assert sprint_data["name"] == sample_sprint.name

        # Check members data
        assert len(data["members"]) >= 1
        member = data["members"][0]
        assert member["member_id"] == alice.member_id
        assert member["name"] == alice.name
        assert "days" in member
        assert "sum_days" in member
        assert "sum_hours" in member

    def test_get_sprint_availability_not_found(self, db_session):
        """Test: GET /sprints/{sprint_id}/availability - Sprint not found (404)"""
        response = client.get(f"{API_BASE}/sprints/99999/availability")

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_patch_availability_override_success(self, db_session, sample_sprint, sample_members):
        """Test: PATCH /sprints/{sprint_id}/availability - Success case"""
        # Setup: Add roster entry
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()

        # Override data
        override_data = {
            "member_id": alice.member_id,
            "day": "2025-10-27",  # Within sprint range
            "state": "half",
            "reason": "Doctor appointment"
        }

        # Act: API call
        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability",
            json=override_data
        )

        # Assert: Success response
        assert response.status_code == 200
        assert response.json()["message"] == "Override updated successfully"

        # Verify override was created in DB
        override = db_session.query(AvailabilityOverride).filter_by(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=date(2025, 10, 27)
        ).first()
        assert override is not None
        assert override.state == AvailabilityState.HALF
        assert override.reason == "Doctor appointment"

    def test_patch_availability_sprint_not_found(self, db_session):
        """Test: PATCH /sprints/{sprint_id}/availability - Sprint not found (404)"""
        override_data = {
            "member_id": 1,
            "day": "2025-10-27",
            "state": "half",
            "reason": "Test"
        }

        response = client.patch(f"{API_BASE}/sprints/99999/availability", json=override_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_patch_availability_day_out_of_range(self, db_session, sample_sprint, sample_members):
        """Test: PATCH /sprints/{sprint_id}/availability - Day outside sprint range (422)"""
        # Setup: Add roster entry
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()

        # Try day outside sprint range
        override_data = {
            "member_id": alice.member_id,
            "day": "2024-01-01",  # Way outside sprint range
            "state": "half",
            "reason": "Test"
        }

        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability",
            json=override_data
        )

        assert response.status_code == 422
        assert "is not within sprint range" in response.json()["detail"]

    def test_patch_availability_bulk_success(self, db_session, sample_sprint, sample_members):
        """Test: PATCH /sprints/{sprint_id}/availability/bulk - Success case"""
        # Setup: Add roster entries for multiple members
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        rosters = [
            SprintRoster(sprint_id=sample_sprint.sprint_id, member_id=alice.member_id, allocation=1.0),
            SprintRoster(sprint_id=sample_sprint.sprint_id, member_id=bogdan.member_id, allocation=0.8)
        ]
        db_session.add_all(rosters)
        db_session.commit()

        # Bulk override data
        bulk_data = [
            {
                "member_id": alice.member_id,
                "day": "2025-10-27",
                "state": "half",
                "reason": "Doctor appointment"
            },
            {
                "member_id": bogdan.member_id,
                "day": "2025-10-27",
                "state": "unavailable",
                "reason": "Sick leave"
            }
        ]

        # Act: API call
        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability/bulk",
            json=bulk_data
        )

        # Assert: Success response
        assert response.status_code == 200
        data = response.json()
        assert data["success_count"] == 2
        assert data["error_count"] == 0
        assert len(data["results"]) == 2
        assert len(data["errors"]) == 0

        # Verify overrides were created
        overrides = db_session.query(AvailabilityOverride).filter_by(
            sprint_id=sample_sprint.sprint_id
        ).all()
        assert len(overrides) == 2

    def test_patch_availability_bulk_sprint_not_found(self, db_session):
        """Test: PATCH /sprints/{sprint_id}/availability/bulk - Sprint not found (404)"""
        bulk_data = [
            {
                "member_id": 1,
                "day": "2025-10-27",
                "state": "half",
                "reason": "Test"
            }
        ]

        response = client.patch(f"{API_BASE}/sprints/99999/availability/bulk", json=bulk_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"


class TestWorkingSprintsAPI:
    """Sprint API tests that work with actual Sprint model"""

    def test_get_sprint_by_id_success(self, db_session, sample_sprint):
        """Test: GET /sprints/{sprint_id} - Success case"""
        response = client.get(f"{API_BASE}/sprints/{sample_sprint.sprint_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["sprint_id"] == sample_sprint.sprint_id
        assert data["name"] == sample_sprint.name
        assert data["start_date"] == sample_sprint.start_date.isoformat()
        assert data["end_date"] == sample_sprint.end_date.isoformat()
        # Note: API returns string, model has enum - this test reveals the issue
        assert data["status"] in ["planned", "active", "finished"]

    def test_get_sprint_by_id_not_found(self, db_session):
        """Test: GET /sprints/{sprint_id} - Sprint not found (404)"""
        response = client.get(f"{API_BASE}/sprints/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_list_sprints_success(self, db_session, sample_sprint):
        """Test: GET /sprints/ - Success case"""
        response = client.get(f"{API_BASE}/sprints/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check first sprint structure
        sprint_data = data[0]
        required_fields = ["sprint_id", "name", "start_date", "end_date", "status"]
        for field in required_fields:
            assert field in sprint_data

    def test_create_sprint_success(self, db_session):
        """Test: POST /sprints/ - Success case"""
        sprint_data = {
            "name": "API Test Sprint",
            "start_date": "2025-12-01",
            "end_date": "2025-12-14"
        }

        response = client.post(f"{API_BASE}/sprints/", json=sprint_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sprint_data["name"]
        assert data["start_date"] == sprint_data["start_date"]
        assert data["end_date"] == sprint_data["end_date"]
        assert "sprint_id" in data
        assert data["status"] == "planned"  # Default status

        # Verify in database
        created_sprint = db_session.query(Sprint).filter_by(name="API Test Sprint").first()
        assert created_sprint is not None

    def test_update_sprint_success(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id} - Success case"""
        update_data = {
            "name": "Updated Sprint Name"
        }

        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["sprint_id"] == sample_sprint.sprint_id

        # Verify in database (refresh session to see changes)
        db_session.expire_all()
        updated_sprint = db_session.get(Sprint, sample_sprint.sprint_id)
        assert updated_sprint.name == update_data["name"]

    def test_delete_sprint_success(self, db_session):
        """Test: DELETE /sprints/{sprint_id} - Success case"""
        # Create a sprint to delete
        sprint = Sprint(
            name="Delete Test Sprint",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 14)
        )
        db_session.add(sprint)
        db_session.commit()
        sprint_id = sprint.sprint_id

        response = client.delete(f"{API_BASE}/sprints/{sprint_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Sprint deleted successfully"

        # Verify deletion by making another API call (DB transaction isolation)
        verify_response = client.get(f"{API_BASE}/sprints/{sprint_id}")
        assert verify_response.status_code == 404


class TestWorkingMembersAPI:
    """Member API tests that work with actual Member model"""

    def test_get_member_by_id_success(self, db_session, sample_members):
        """Test: GET /members/{member_id} - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        response = client.get(f"{API_BASE}/members/{alice.member_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == alice.member_id
        assert data["name"] == alice.name
        assert float(data["employment_ratio"]) == float(alice.employment_ratio)
        assert data["region_code"] == alice.region_code
        # Note: Member model has 'active' field, not 'is_active'

    def test_get_member_by_id_not_found(self, db_session):
        """Test: GET /members/{member_id} - Member not found (404)"""
        response = client.get(f"{API_BASE}/members/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Member not found"

    def test_list_members_success(self, db_session, sample_members):
        """Test: GET /members/ - Success case"""
        response = client.get(f"{API_BASE}/members/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # We have 3 sample members

        # Check member structure
        member_data = data[0]
        required_fields = ["member_id", "name", "employment_ratio", "region_code"]
        for field in required_fields:
            assert field in member_data

    def test_create_member_success(self, db_session):
        """Test: POST /members/ - Success case"""
        member_data = {
            "name": "API Test Member",
            "employment_ratio": 0.8,
            "region_code": "DE-NW"
        }

        response = client.post(f"{API_BASE}/members/", json=member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == member_data["name"]
        assert float(data["employment_ratio"]) == member_data["employment_ratio"]
        assert data["region_code"] == member_data["region_code"]
        assert "member_id" in data

        # Verify in database
        created_member = db_session.query(Member).filter_by(name="API Test Member").first()
        assert created_member is not None

    def test_update_member_success(self, db_session, sample_members):
        """Test: PUT /members/{member_id} - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        update_data = {
            "name": "Alice Updated API",
            "employment_ratio": 0.9,
            "region_code": "DE-BY"
        }

        response = client.put(f"{API_BASE}/members/{alice.member_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert float(data["employment_ratio"]) == update_data["employment_ratio"]
        assert data["region_code"] == update_data["region_code"]
        assert data["member_id"] == alice.member_id

    def test_delete_member_success(self, db_session, sample_members):
        """Test: DELETE /members/{member_id} - Success case (deactivation)"""
        carol = next(m for m in sample_members if m.name == "Carol Smith")
        member_id = carol.member_id

        response = client.delete(f"{API_BASE}/members/{member_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Member deactivated successfully"

        # Verify member is deactivated by checking API response
        # (DB transaction isolation makes direct DB check unreliable in tests)
        verify_response = client.get(f"{API_BASE}/members/?include_inactive=true")
        assert verify_response.status_code == 200
        members = verify_response.json()
        deactivated_member = next((m for m in members if m['member_id'] == member_id), None)
        assert deactivated_member is not None
        assert deactivated_member['active'] == False
