#!/usr/bin/env python3
"""
Seed Script für Capacity Planner - lädt Beispiel-Daten

Erstellt:
- 2 Members: Alice (DE-NW), Bogdan (UA)
- 1 Sprint (Draft): W43 über 2 Wochen
- Feiertage: DE-NW (Reformationstag), UA
- PTO: 1 Tag für Alice
- Roster: beide mit allocation 1.0
"""

import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models import (
    Member, Sprint, SprintStatus, SprintRoster,
    PTO, Holiday, AvailabilityOverride, AvailabilityState
)


def create_seed_data():
    """Erstelle Seed-Daten für Demo und Tests"""
    db: Session = SessionLocal()

    try:
        # Check if data already exists
        if db.query(Member).count() > 0:
            print("🔄 Seed-Daten bereits vorhanden, überspringe...")
            return

        print("🌱 Erstelle Seed-Daten...")

        # === Members ===
        alice = Member(
            name="Alice Schmidt",
            employment_ratio=Decimal("1.0"),
            region_code="DE-NW",
            active=True
        )

        bogdan = Member(
            name="Bogdan Petrov",
            employment_ratio=Decimal("1.0"),
            region_code="UA",
            active=True
        )

        db.add_all([alice, bogdan])
        db.flush()  # Flush to get IDs

        print(f"✅ Members erstellt: {alice.name} (ID: {alice.member_id}), {bogdan.name} (ID: {bogdan.member_id})")

        # === Sprint W43 (2 Wochen: 21.10.2025 - 01.11.2025) ===
        sprint_start = date(2025, 10, 21)  # Dienstag
        sprint_end = date(2025, 11, 1)     # Samstag (2 Wochen später)

        sprint = Sprint(
            name="Sprint W43-44 2025",
            start_date=sprint_start,
            end_date=sprint_end,
            status=SprintStatus.DRAFT
        )

        db.add(sprint)
        db.flush()

        print(f"✅ Sprint erstellt: {sprint.name} (ID: {sprint.sprint_id}, {sprint_start} - {sprint_end})")

        # === Sprint Roster ===
        roster_alice = SprintRoster(
            sprint_id=sprint.sprint_id,
            member_id=alice.member_id,
            allocation=Decimal("1.0")
        )

        roster_bogdan = SprintRoster(
            sprint_id=sprint.sprint_id,
            member_id=bogdan.member_id,
            allocation=Decimal("1.0")
        )

        db.add_all([roster_alice, roster_bogdan])

        print("✅ Sprint Roster erstellt: Alice und Bogdan mit 100% Allocation")

        # === Feiertage ===
        holidays = []

        # DE-NW: Reformationstag (31.10.2025)
        reformationstag = Holiday(
            date=date(2025, 10, 31),
            region_code="DE-NW",
            name="Reformationstag",
            is_company_day=True
        )
        holidays.append(reformationstag)

        # UA: День української писемності та мови (09.11.2025 - außerhalb Sprint aber als Beispiel)
        # Nehmen wir einen Feiertag im Sprint-Zeitraum: Tag der Befreiung Kiews (6.11 -> 25.10 für Demo)
        ua_holiday = Holiday(
            date=date(2025, 10, 25),
            region_code="UA",
            name="Tag der Befreiung Kiews",
            is_company_day=True
        )
        holidays.append(ua_holiday)

        db.add_all(holidays)

        print("✅ Feiertage erstellt: Reformationstag (DE-NW), Tag der Befreiung Kiews (UA)")

        # === PTO ===
        # Alice hat 1 Tag Urlaub am 28.10.2025 (Dienstag)
        alice_pto = PTO(
            member_id=alice.member_id,
            from_date=date(2025, 10, 28),
            to_date=date(2025, 10, 28),
            type="vacation",
            notes="Persönlicher Urlaubstag"
        )

        db.add(alice_pto)

        print("✅ PTO erstellt: Alice hat Urlaub am 28.10.2025")

        # === Availability Overrides (Beispiel) ===
        # Bogdan ist am 30.10.2025 nur halbtags verfügbar
        bogdan_override = AvailabilityOverride(
            sprint_id=sprint.sprint_id,
            member_id=bogdan.member_id,
            day=date(2025, 10, 30),
            state=AvailabilityState.HALF,
            reason="Arzttermin am Nachmittag"
        )

        db.add(bogdan_override)

        print("✅ Availability Override erstellt: Bogdan halbtags am 30.10.2025")

        # Commit all changes
        db.commit()

        print("\n🎉 Seed-Daten erfolgreich erstellt!")
        print("\n📊 Zusammenfassung:")
        print(f"   - {db.query(Member).count()} Members")
        print(f"   - {db.query(Sprint).count()} Sprints")
        print(f"   - {db.query(SprintRoster).count()} Sprint Roster Einträge")
        print(f"   - {db.query(Holiday).count()} Feiertage")
        print(f"   - {db.query(PTO).count()} PTO Einträge")
        print(f"   - {db.query(AvailabilityOverride).count()} Availability Overrides")

    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Seed-Daten: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
