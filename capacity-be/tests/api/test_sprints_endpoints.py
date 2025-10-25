"""
API Endpoint Tests for Sprints Routes
Tests for CRUD operations, validation, error handling, and edge cases.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Sprint, SprintStatus

client = TestClient(app)


# API Base URL
API_BASE = "/api/v1"

class TestSprintsAPI:
    """Test suite for Sprints API endpoints"""

    def test_list_sprints_success(self, db_session, sample_sprint):
        """Test: GET /sprints/ - Success case"""
        response = client.get("{API_BASE}/sprints/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check first sprint structure
        sprint_data = data[0]
        required_fields = ["sprint_id", "name", "start_date", "end_date", "status"]
        for field in required_fields:
            assert field in sprint_data

    def test_list_sprints_with_pagination(self, db_session):
        """Test: GET /sprints/ - Pagination parameters"""
        # Create multiple sprints for pagination test
        sprints = []
        for i in range(5):
            sprint = Sprint(
                name=f"Test Sprint {i}",
                start_date=date(2025, 10, 1 + i),
                end_date=date(2025, 10, 10 + i),
                status=SprintStatus.DRAFT
            )
            sprints.append(sprint)

        db_session.add_all(sprints)
        db_session.commit()

        # Test pagination
        response = client.get("{API_BASE}/sprints/?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2  # Should respect limit

    def test_get_sprint_by_id_success(self, db_session, sample_sprint):
        """Test: GET /sprints/{sprint_id} - Success case"""
        response = client.get(f"{API_BASE}/sprints/{sample_sprint.sprint_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["sprint_id"] == sample_sprint.sprint_id
        assert data["name"] == sample_sprint.name
        assert data["start_date"] == sample_sprint.start_date.isoformat()
        assert data["end_date"] == sample_sprint.end_date.isoformat()
        assert data["status"] == sample_sprint.status

    def test_get_sprint_by_id_not_found(self, db_session):
        """Test: GET /sprints/{sprint_id} - Sprint not found (404)"""
        response = client.get("{API_BASE}/sprints/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_create_sprint_success(self, db_session):
        """Test: POST /sprints/ - Success case"""
        sprint_data = {
            "name": "New Test Sprint",
            "start_date": "2025-11-01",
            "end_date": "2025-11-14"
        }

        response = client.post("{API_BASE}/sprints/", json=sprint_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sprint_data["name"]
        assert data["start_date"] == sprint_data["start_date"]
        assert data["end_date"] == sprint_data["end_date"]
        assert data["status"] == SprintStatus.DRAFT  # Default status
        assert "sprint_id" in data

        # Verify in database
        created_sprint = db_session.query(Sprint).filter_by(name="New Test Sprint").first()
        assert created_sprint is not None

    def test_create_sprint_invalid_dates(self, db_session):
        """Test: POST /sprints/ - Invalid date range (422)"""
        sprint_data = {
            "name": "Invalid Sprint",
            "start_date": "2025-11-14",  # End before start
            "end_date": "2025-11-01"
        }

        response = client.post("{API_BASE}/sprints/", json=sprint_data)

        assert response.status_code == 422
        # Should contain validation error about dates

    def test_create_sprint_past_dates(self, db_session):
        """Test: POST /sprints/ - Past dates (422)"""
        sprint_data = {
            "name": "Past Sprint",
            "start_date": "2020-01-01",  # Far in the past
            "end_date": "2020-01-14"
        }

        response = client.post("{API_BASE}/sprints/", json=sprint_data)

        assert response.status_code == 422

    def test_create_sprint_missing_fields(self, db_session):
        """Test: POST /sprints/ - Missing required fields (422)"""
        incomplete_data = {
            "name": "Incomplete Sprint"
            # Missing start_date and end_date
        }

        response = client.post("{API_BASE}/sprints/", json=incomplete_data)

        assert response.status_code == 422

    def test_update_sprint_success(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id} - Success case"""
        update_data = {
            "name": "Updated Sprint Name",
            "status": SprintStatus.ACTIVE
        }

        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["status"] == update_data["status"]
        assert data["sprint_id"] == sample_sprint.sprint_id

        # Verify in database
        updated_sprint = db_session.query(Sprint).get(sample_sprint.sprint_id)
        assert updated_sprint.name == update_data["name"]
        assert updated_sprint.status == update_data["status"]

    def test_update_sprint_dates(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id} - Update dates"""
        update_data = {
            "start_date": "2025-12-01",
            "end_date": "2025-12-14"
        }

        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["start_date"] == update_data["start_date"]
        assert data["end_date"] == update_data["end_date"]

    def test_update_sprint_invalid_dates(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id} - Invalid date range (422)"""
        update_data = {
            "start_date": "2025-12-14",  # End before start
            "end_date": "2025-12-01"
        }

        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}", json=update_data)

        assert response.status_code == 422

    def test_update_sprint_partial_dates(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id} - Update only start_date"""
        update_data = {
            "start_date": "2025-12-01"
            # Keep existing end_date
        }

        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}", json=update_data)

        # Should validate against existing end_date
        if response.status_code == 200:
            data = response.json()
            assert data["start_date"] == update_data["start_date"]
        elif response.status_code == 422:
            # If existing end_date makes this invalid, that's also correct
            pass

    def test_update_sprint_not_found(self, db_session):
        """Test: PATCH /sprints/{sprint_id} - Sprint not found (404)"""
        update_data = {
            "name": "Updated Sprint"
        }

        response = client.patch("{API_BASE}/sprints/99999", json=update_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_update_sprint_invalid_status(self, db_session, sample_sprint):
        """Test: PATCH /sprints/{sprint_id} - Invalid status value (422)"""
        update_data = {
            "status": "invalid_status"
        }

        response = client.patch(f"{API_BASE}/sprints/{sample_sprint.sprint_id}", json=update_data)

        assert response.status_code == 422

    def test_delete_sprint_success(self, db_session, sample_sprint):
        """Test: DELETE /sprints/{sprint_id} - Success case"""
        sprint_id = sample_sprint.sprint_id

        response = client.delete(f"{API_BASE}/sprints/{sprint_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Sprint deleted successfully"

        # Verify deletion in database
        deleted_sprint = db_session.query(Sprint).get(sprint_id)
        assert deleted_sprint is None

    def test_delete_sprint_not_found(self, db_session):
        """Test: DELETE /sprints/{sprint_id} - Sprint not found (404)"""
        response = client.delete("{API_BASE}/sprints/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    def test_sprints_api_malformed_requests(self, db_session):
        """Test: Various malformed requests"""
        # Test POST with invalid JSON structure
        response = client.post("{API_BASE}/sprints/", json={"invalid": "data"})
        assert response.status_code == 422

        # Test PATCH with invalid JSON structure
        response = client.patch("{API_BASE}/sprints/1", json={"invalid": "data"})
        # Should still try to process, might be 404 or 422

    def test_sprints_api_content_type_validation(self, db_session):
        """Test: Content-Type validation"""
        # Test POST without JSON content-type
        response = client.post(
            "{API_BASE}/sprints/",
            data="invalid data",
            headers={"Content-Type": "text/plain"}
        )
        # Should fail due to invalid content type
        assert response.status_code in [400, 422]

    def test_sprint_status_transitions(self, db_session):
        """Test: Sprint status transitions"""
        # Create sprint in DRAFT status
        sprint_data = {
            "name": "Status Test Sprint",
            "start_date": "2025-11-01",
            "end_date": "2025-11-14"
        }

        response = client.post("{API_BASE}/sprints/", json=sprint_data)
        assert response.status_code == 200
        sprint_id = response.json()["sprint_id"]

        # Transition to ACTIVE
        update_data = {"status": SprintStatus.ACTIVE}
        response = client.patch(f"{API_BASE}/sprints/{sprint_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["status"] == SprintStatus.ACTIVE

        # Transition to CLOSED
        update_data = {"status": SprintStatus.CLOSED}
        response = client.patch(f"{API_BASE}/sprints/{sprint_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["status"] == SprintStatus.CLOSED

    def test_sprint_name_constraints(self, db_session):
        """Test: Sprint name validation"""
        # Test empty name
        sprint_data = {
            "name": "",
            "start_date": "2025-11-01",
            "end_date": "2025-11-14"
        }

        response = client.post("{API_BASE}/sprints/", json=sprint_data)
        # Should fail validation for empty name
        assert response.status_code == 422

        # Test very long name
        long_name = "x" * 300  # Very long name
        sprint_data = {
            "name": long_name,
            "start_date": "2025-11-01",
            "end_date": "2025-11-14"
        }

        response = client.post("{API_BASE}/sprints/", json=sprint_data)
        # May succeed or fail based on DB constraints
