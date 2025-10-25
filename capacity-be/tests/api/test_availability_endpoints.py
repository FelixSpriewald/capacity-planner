"""
Comprehensive API Endpoint Tests for Availability Routes
Tests focusing on HTTP responses, error handling, validation, and edge cases.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Sprint, Member, SprintRoster, AvailabilityOverride, AvailabilityState

client = TestClient(app)

# API Base URL
API_BASE = "/api/v1"


class TestAvailabilityAPI:
    """Test suite for Availability API endpoints"""

    def test_get_sprint_availability_success(self, db_session, sample_sprint, sample_members):
        """Test: GET /sprints/{sprint_id}/availability - Success case"""
        # Setup: Add roster entries
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

        # Assert: Success response
        assert response.status_code == 200
        data = response.json()

        assert "sprint" in data
        assert "members" in data
        assert "summary" in data
        assert data["sprint"]["sprint_id"] == sample_sprint.sprint_id
        assert data["sprint"]["name"] == sample_sprint.name
        assert len(data["members"]) == 1
        assert data["members"][0]["member_id"] == alice.member_id

    def test_get_sprint_availability_not_found(self, db_session):
        """Test: GET /sprints/{sprint_id}/availability - Sprint not found (404)"""
        non_existent_id = 99999

        response = client.get(f"{API_BASE}/sprints/{non_existent_id}/availability")

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
            "day": "2025-10-30",  # Within sprint range
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
            day=date(2025, 10, 30)
        ).first()
        assert override is not None
        assert override.state == AvailabilityState.HALF
        assert override.reason == "Doctor appointment"

    def test_patch_availability_override_delete(self, db_session, sample_sprint, sample_members):
        """Test: PATCH /sprints/{sprint_id}/availability - Delete override (state=null)"""
        # Setup: Add roster entry and existing override
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        existing_override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=date(2025, 10, 30),
            state=AvailabilityState.HALF,
            reason="Existing override"
        )
        db_session.add_all([roster, existing_override])
        db_session.commit()

        # Delete override data (state=null)
        override_data = {
            "member_id": alice.member_id,
            "day": "2025-10-30",
            "state": None,  # Delete override
            "reason": None
        }

        # Act: API call
        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability",
            json=override_data
        )

        # Assert: Success response
        assert response.status_code == 200
        assert response.json()["message"] == "Override updated successfully"

        # Verify override was deleted from DB
        override = db_session.query(AvailabilityOverride).filter_by(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=date(2025, 10, 30)
        ).first()
        assert override is None

    def test_patch_availability_sprint_not_found(self, db_session):
        """Test: PATCH /sprints/{sprint_id}/availability - Sprint not found (404)"""
        override_data = {
            "member_id": 1,
            "day": "2025-10-30",
            "state": "half",
            "reason": "Test"
        }

        response = client.patch("{API_BASE}/sprints/99999/availability", json=override_data)

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

    def test_patch_availability_member_not_in_roster(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id}/availability - Member not in roster (422)"""
        # No roster entries added for this sprint

        override_data = {
            "member_id": 99999,  # Non-existent or not in roster
            "day": "2025-10-30",
            "state": "half",
            "reason": "Test"
        }

        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability",
            json=override_data
        )

        assert response.status_code == 422
        assert "is not in sprint roster" in response.json()["detail"]

    def test_patch_availability_invalid_state(self, db_session, sample_sprint, sample_members):
        """Test: PATCH /sprints/{sprint_id}/availability - Invalid state value (422)"""
        # Setup: Add roster entry
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()

        # Invalid state value
        override_data = {
            "member_id": alice.member_id,
            "day": "2025-10-30",
            "state": "invalid_state",  # Invalid
            "reason": "Test"
        }

        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability",
            json=override_data
        )

        # Should fail validation (422 or 400)
        assert response.status_code in [400, 422]

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
                "day": "2025-10-30",
                "state": "half",
                "reason": "Doctor appointment"
            },
            {
                "member_id": bogdan.member_id,
                "day": "2025-10-31",
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

    def test_patch_availability_bulk_partial_errors(self, db_session, sample_sprint, sample_members):
        """Test: PATCH /sprints/{sprint_id}/availability/bulk - Partial errors"""
        # Setup: Add roster entry for only one member
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        roster = SprintRoster(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            allocation=1.0
        )
        db_session.add(roster)
        db_session.commit()

        # Bulk data with one valid and one invalid entry
        bulk_data = [
            {
                "member_id": alice.member_id,
                "day": "2025-10-30",
                "state": "half",
                "reason": "Valid override"
            },
            {
                "member_id": 99999,  # Invalid member
                "day": "2025-10-31",
                "state": "unavailable",
                "reason": "Invalid member"
            }
        ]

        # Act: API call
        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability/bulk",
            json=bulk_data
        )

        # Assert: Partial success response
        assert response.status_code == 200
        data = response.json()
        assert data["success_count"] == 1
        assert data["error_count"] == 1
        assert len(data["results"]) == 1
        assert len(data["errors"]) == 1

    def test_patch_availability_bulk_sprint_not_found(self, db_session):
        """Test: PATCH /sprints/{sprint_id}/availability/bulk - Sprint not found (404)"""
        bulk_data = [
            {
                "member_id": 1,
                "day": "2025-10-30",
                "state": "half",
                "reason": "Test"
            }
        ]

        response = client.patch("{API_BASE}/sprints/99999/availability/bulk", json=bulk_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_availability_api_malformed_json(self, db_session, sample_sprint):
        """Test: API endpoints with malformed JSON (400)"""
        # Test single PATCH with invalid JSON structure
        response = client.patch(
            f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability",
            json={"invalid": "structure"}  # Missing required fields
        )

        # Should fail validation
        assert response.status_code == 422

    def test_availability_api_empty_request_body(self, db_session, sample_sprint):
        """Test: API endpoints with empty request body"""
        # Test PATCH with empty body
        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability")

        # Should fail due to missing request body
        assert response.status_code == 422

    def test_availability_response_structure(self, db_session, sample_sprint, sample_members):
        """Test: GET /sprints/{sprint_id}/availability - Response structure validation"""
        # Setup: Complex scenario with multiple members, overrides, etc.
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        bogdan = next(m for m in sample_members if m.name == "Bogdan Ivanov")

        rosters = [
            SprintRoster(sprint_id=sample_sprint.sprint_id, member_id=alice.member_id, allocation=1.0),
            SprintRoster(sprint_id=sample_sprint.sprint_id, member_id=bogdan.member_id, allocation=0.8)
        ]

        override = AvailabilityOverride(
            sprint_id=sample_sprint.sprint_id,
            member_id=alice.member_id,
            day=date(2025, 10, 30),
            state=AvailabilityState.HALF,
            reason="Test override"
        )

        db_session.add_all(rosters + [override])
        db_session.commit()

        # Act: API call
        response = client.get(f"{API_BASE}/sprints/{sample_sprint.sprint_id}/availability")

        # Assert: Detailed response structure
        assert response.status_code == 200
        data = response.json()

        # Sprint structure
        assert "sprint" in data
        sprint_data = data["sprint"]
        required_sprint_fields = ["sprint_id", "name", "start_date", "end_date", "status"]
        for field in required_sprint_fields:
            assert field in sprint_data

        # Members structure
        assert "members" in data
        assert len(data["members"]) == 2
        member_data = data["members"][0]
        required_member_fields = ["member_id", "name", "employment_ratio", "allocation",
                                "allocation_percentage", "days", "sum_days", "sum_hours"]
        for field in required_member_fields:
            assert field in member_data

        # Days structure
        assert "days" in member_data
        assert len(member_data["days"]) > 0
        day_data = member_data["days"][0]
        required_day_fields = ["date", "auto_state", "override_state", "final_state",
                             "is_weekend", "is_holiday", "is_pto", "in_assignment"]
        for field in required_day_fields:
            assert field in day_data

        # Summary structure
        assert "summary" in data
        summary_data = data["summary"]
        required_summary_fields = ["working_days", "total_capacity_hours", "total_capacity_days",
                                 "available_capacity_hours", "available_capacity_days",
                                 "efficiency", "holidays_by_region", "sum_days_team"]
        for field in required_summary_fields:
            assert field in summary_data
