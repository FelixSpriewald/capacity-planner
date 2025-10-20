"""
Pytest Configuration and Fixtures

Test-Setup für die Capacity Planner API Tests
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import get_db, Base
from app.db.models import Member, Sprint, SprintRoster, PTO, AvailabilityOverride, Holiday


# Test Database Setup (SQLite in Memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Database dependency override für Tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Test Database Session Fixture"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Test Client Fixture"""
    return TestClient(app)


@pytest.fixture(scope="function")
def sample_members(db_session):
    """Fixture für Beispiel-Members"""
    members = [
        Member(
            name="Alice Mueller",
            employment_ratio=1.0,
            region_code="DE-NW",
            active=True
        ),
        Member(
            name="Bogdan Ivanov", 
            employment_ratio=0.75,
            region_code="UA",
            active=True
        ),
        Member(
            name="Carol Smith",
            employment_ratio=0.5,
            region_code=None,  # No region
            active=True
        )
    ]
    
    for member in members:
        db_session.add(member)
    db_session.commit()
    
    for member in members:
        db_session.refresh(member)
    
    return members


@pytest.fixture
def sample_sprint(db_session, sample_members):
    sprint = Sprint(
        name="Sample Sprint",
        start_date=date(2025, 10, 27),  # Start late October
        end_date=date(2025, 11, 7),     # End early November (includes Nov 1st)
        status="ACTIVE"
    )
    db_session.add(sprint)
    db_session.commit()
    db_session.refresh(sprint)
    return sprint


@pytest.fixture(scope="function")
def sample_holidays(db_session):
    """Fixture für Beispiel-Feiertage"""
    holidays = [
        Holiday(
            name="Allerheiligen",
            date=date(2025, 11, 1),
            region_code="DE-NW"
        ),
        Holiday(
            name="Ukrainian Independence Day",
            date=date(2025, 8, 24),
            region_code="UA"
        )
    ]
    
    for holiday in holidays:
        db_session.add(holiday)
    db_session.commit()
    
    return holidays