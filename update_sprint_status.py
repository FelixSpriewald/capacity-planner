#!/usr/bin/env python3
"""
Script to update sprint status enum values and recalculate status based on dates
"""

import sys
import os
from datetime import date

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'capacity-be'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models.sprints import Sprint
from app.db.crud.sprints import calculate_status_from_dates

# Database configuration
DATABASE_URL = "sqlite:///./capacity_planner.db"

def update_sprint_statuses():
    """Update sprint status enum values and recalculate based on dates"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as db:
        try:
            print("Updating sprint status enum values...")

            # Update enum values in database
            # First, let's see what statuses we have
            result = db.execute(text("SELECT DISTINCT status FROM sprints")).fetchall()
            print(f"Current statuses: {[row[0] for row in result]}")

            # Update 'draft' to 'planned'
            updated_draft = db.execute(text("UPDATE sprints SET status = 'planned' WHERE status = 'draft'")).rowcount
            print(f"Updated {updated_draft} sprints from 'draft' to 'planned'")

            # Now recalculate all statuses based on dates
            sprints = db.query(Sprint).all()
            updated_count = 0

            for sprint in sprints:
                old_status = sprint.status
                calculated_status = calculate_status_from_dates(sprint.start_date, sprint.end_date)

                if str(sprint.status).split('.')[-1] != calculated_status.value:
                    sprint.status = calculated_status
                    updated_count += 1
                    print(f"Sprint '{sprint.name}': {old_status} -> {calculated_status.value}")

            db.commit()
            print(f"\nSuccessfully updated {updated_count} sprint statuses based on dates")

            # Show final status distribution
            result = db.execute(text("SELECT status, COUNT(*) FROM sprints GROUP BY status")).fetchall()
            print("\nFinal status distribution:")
            for status, count in result:
                print(f"  {status}: {count}")

        except Exception as e:
            print(f"Error updating sprint statuses: {e}")
            db.rollback()
            return False

    return True

if __name__ == "__main__":
    print("Starting sprint status update...")
    success = update_sprint_statuses()
    if success:
        print("Sprint status update completed successfully!")
    else:
        print("Sprint status update failed!")
        sys.exit(1)
