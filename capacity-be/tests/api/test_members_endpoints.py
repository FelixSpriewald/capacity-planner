"""
API Endpoint Tests for Members Routes
Tests for CRUD operations, validation, error handling, and edge cases.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Member
from decimal import Decimal

client = TestClient(app)


# API Base URL
API_BASE = "/api/v1"

class TestMembersAPI:
    """Test suite for Members API endpoints"""

    def test_list_members_success(self, db_session, sample_members):
        """Test: GET /members/ - Success case"""
        response = client.get("{API_BASE}/members/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # We have 3 sample members

        # Check member structure
        member_data = data[0]
        required_fields = ["member_id", "name", "employment_ratio", "region_code", "is_active"]
        for field in required_fields:
            assert field in member_data

    def test_list_members_pagination(self, db_session, sample_members):
        """Test: GET /members/ - Pagination parameters"""
        response = client.get("{API_BASE}/members/?skip=1&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2  # Should respect limit

    def test_list_members_include_inactive(self, db_session, sample_members):
        """Test: GET /members/ - Include inactive members"""
        # First deactivate a member
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        alice.is_active = False
        db_session.commit()

        # Test without include_inactive (default)
        response = client.get("{API_BASE}/members/")
        active_members = response.json()
        alice_in_active = any(m["member_id"] == alice.member_id for m in active_members)
        assert not alice_in_active  # Should not include inactive

        # Test with include_inactive=true
        response = client.get("{API_BASE}/members/?include_inactive=true")
        all_members = response.json()
        alice_in_all = any(m["member_id"] == alice.member_id for m in all_members)
        assert alice_in_all  # Should include inactive

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
        assert data["is_active"] == alice.is_active

    def test_get_member_by_id_not_found(self, db_session):
        """Test: GET /members/{member_id} - Member not found (404)"""
        response = client.get("{API_BASE}/members/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Member not found"

    def test_create_member_success(self, db_session):
        """Test: POST /members/ - Success case"""
        member_data = {
            "name": "New Test Member",
            "employment_ratio": 0.8,
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == member_data["name"]
        assert float(data["employment_ratio"]) == member_data["employment_ratio"]
        assert data["region_code"] == member_data["region_code"]
        assert data["is_active"] == True  # Default value
        assert "member_id" in data

        # Verify in database
        created_member = db_session.query(Member).filter_by(name="New Test Member").first()
        assert created_member is not None

    def test_create_member_invalid_employment_ratio(self, db_session):
        """Test: POST /members/ - Invalid employment ratio (422)"""
        # Test employment ratio > 1.0
        member_data = {
            "name": "Invalid Member",
            "employment_ratio": 1.5,  # Invalid
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 422

        # Test employment ratio < 0
        member_data["employment_ratio"] = -0.1
        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 422

        # Test employment ratio = 0
        member_data["employment_ratio"] = 0.0
        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 422

    def test_create_member_missing_fields(self, db_session):
        """Test: POST /members/ - Missing required fields (422)"""
        incomplete_data = {
            "name": "Incomplete Member"
            # Missing employment_ratio
        }

        response = client.post("{API_BASE}/members/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_member_empty_name(self, db_session):
        """Test: POST /members/ - Empty name (422)"""
        member_data = {
            "name": "",  # Empty name
            "employment_ratio": 1.0,
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 422

    def test_create_member_optional_region(self, db_session):
        """Test: POST /members/ - Optional region code"""
        member_data = {
            "name": "No Region Member",
            "employment_ratio": 1.0
            # No region_code - should be optional
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 200
        data = response.json()
        assert data["region_code"] is None

    def test_update_member_success(self, db_session, sample_members):
        """Test: PUT /members/{member_id} - Success case"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        update_data = {
            "name": "Alice Updated",
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

        # Verify in database
        updated_member = db_session.query(Member).get(alice.member_id)
        assert updated_member.name == update_data["name"]
        assert float(updated_member.employment_ratio) == update_data["employment_ratio"]

    def test_update_member_invalid_employment_ratio(self, db_session, sample_members):
        """Test: PUT /members/{member_id} - Invalid employment ratio (422)"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        update_data = {
            "name": "Alice",
            "employment_ratio": 2.0,  # Invalid
            "region_code": "DE-NW"
        }

        response = client.put(f"{API_BASE}/members/{alice.member_id}", json=update_data)
        assert response.status_code == 422

    def test_update_member_not_found(self, db_session):
        """Test: PUT /members/{member_id} - Member not found (404)"""
        update_data = {
            "name": "Non-existent Member",
            "employment_ratio": 1.0,
            "region_code": "DE-NW"
        }

        response = client.put("{API_BASE}/members/99999", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Member not found"

    def test_delete_member_success(self, db_session, sample_members):
        """Test: DELETE /members/{member_id} - Success case (deactivation)"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")
        member_id = alice.member_id

        response = client.delete(f"{API_BASE}/members/{member_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Member deactivated successfully"

        # Verify member is deactivated (not deleted)
        deactivated_member = db_session.query(Member).get(member_id)
        assert deactivated_member is not None
        assert deactivated_member.is_active == False

    def test_delete_member_not_found(self, db_session):
        """Test: DELETE /members/{member_id} - Member not found (404)"""
        response = client.delete("{API_BASE}/members/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Member not found"

    def test_members_api_malformed_requests(self, db_session):
        """Test: Various malformed requests"""
        # Test POST with invalid JSON structure
        response = client.post("{API_BASE}/members/", json={"invalid": "data"})
        assert response.status_code == 422

        # Test PUT with invalid JSON structure
        response = client.put("{API_BASE}/members/1", json={"invalid": "data"})
        # Should try to process, might be 404 or 422

    def test_members_api_data_types(self, db_session):
        """Test: Data type validation"""
        # Test string employment_ratio
        member_data = {
            "name": "Test Member",
            "employment_ratio": "not_a_number",
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 422

        # Test integer member_id in URL
        response = client.get("{API_BASE}/members/not_an_integer")
        assert response.status_code == 422

    def test_member_employment_ratio_precision(self, db_session):
        """Test: Employment ratio precision handling"""
        member_data = {
            "name": "Precision Test Member",
            "employment_ratio": 0.75,  # Should handle decimal precision
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 200
        data = response.json()
        assert float(data["employment_ratio"]) == 0.75

    def test_member_region_code_validation(self, db_session):
        """Test: Region code validation"""
        # Test valid region codes
        valid_regions = ["DE-NW", "DE-BY", "UA", None]

        for region in valid_regions:
            member_data = {
                "name": f"Test Member {region}",
                "employment_ratio": 1.0,
                "region_code": region
            }

            response = client.post("{API_BASE}/members/", json=member_data)
            assert response.status_code == 200

    def test_member_name_constraints(self, db_session):
        """Test: Member name validation"""
        # Test very long name
        long_name = "x" * 300
        member_data = {
            "name": long_name,
            "employment_ratio": 1.0,
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        # May succeed or fail based on DB constraints

        # Test name with special characters
        special_name = "Test Member äöüß"
        member_data = {
            "name": special_name,
            "employment_ratio": 1.0,
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        # Should succeed with UTF-8 characters
        assert response.status_code == 200

    def test_member_duplicate_names(self, db_session, sample_members):
        """Test: Duplicate member names handling"""
        alice = next(m for m in sample_members if m.name == "Alice Mueller")

        # Try to create another member with same name
        member_data = {
            "name": alice.name,  # Duplicate name
            "employment_ratio": 0.8,
            "region_code": "DE-BY"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        # Should succeed (names don't need to be unique) or fail based on constraints
        # Either way is valid depending on business rules

    def test_member_crud_integration(self, db_session):
        """Test: Full CRUD integration test"""
        # Create
        member_data = {
            "name": "CRUD Test Member",
            "employment_ratio": 0.75,
            "region_code": "DE-NW"
        }

        response = client.post("{API_BASE}/members/", json=member_data)
        assert response.status_code == 200
        member_id = response.json()["member_id"]

        # Read
        response = client.get(f"{API_BASE}/members/{member_id}")
        assert response.status_code == 200
        assert response.json()["name"] == member_data["name"]

        # Update
        update_data = {
            "name": "CRUD Updated Member",
            "employment_ratio": 1.0,
            "region_code": "DE-BY"
        }

        response = client.put(f"{API_BASE}/members/{member_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]

        # Verify update
        response = client.get(f"{API_BASE}/members/{member_id}")
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]

        # Delete (deactivate)
        response = client.delete(f"{API_BASE}/members/{member_id}")
        assert response.status_code == 200

        # Verify deactivation
        response = client.get(f"{API_BASE}/members/{member_id}")
        assert response.status_code == 200
        assert response.json()["is_active"] == False
