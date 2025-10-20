# Capacity Planner - Single Team

Ein Monorepo für einen Team-Capacity-Planner mit Vue 3 Frontend und FastAPI Backend.

## Komponenten

### Frontend (`capacity-fe/`)
- **Stack**: Vue 3 + TypeScript + Vite + PrimeVue + Pinia + Vue Router
- **Features**: Sprint-Management, Availability-Grid, PTO-Verwaltung
- **Package Manager**: pnpm

### Backend (`capacity-be/`)
- **Stack**: Python FastAPI + SQLAlchemy + Alembic
- **Database**: MySQL 8
- **Features**: REST API für Teams, Sprints, Availability-Berechnung

### Database
- **MySQL 8** mit persistenten Volumes
- **Healthchecks** für zuverlässige Container-Starts

## Entwicklung starten

### Lokale Entwicklung

#### Frontend
```bash
cd capacity-fe
pnpm install
pnpm dev
# Läuft auf http://localhost:5173
```

#### Backend
```bash
cd capacity-be

# Option 1: Mit Setup-Skript (empfohlen)
./start-dev.sh

# Option 2: Manuell
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# .env editieren mit MySQL-URL

# Entwicklungsserver starten
PYTHONPATH=$(pwd) .venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Läuft auf http://localhost:8000
```

### Docker Compose (Komplett-Setup)

```bash
# Alle Services starten (MySQL + Backend + optional Frontend)
docker compose up -d

# Database Migrations und Seed-Daten (beim ersten Start)
docker compose exec api alembic upgrade head
docker compose exec api python seed.py

# Services einzeln starten
docker compose up -d db        # Nur MySQL
docker compose up -d api       # MySQL + Backend
docker compose up -d fe        # Alle Services inkl. Frontend

# Logs verfolgen
docker compose logs -f db      # MySQL Logs
docker compose logs -f api     # Backend Logs
docker compose logs -f fe      # Frontend Logs (falls genutzt)

# Services stoppen
docker compose down

# Mit Volumes löschen (Daten-Reset)
docker compose down -v
```

### API Health Check
Nach dem Start ist die API unter http://localhost:8000/health erreichbar.

### API Endpoints testen
```bash
# Health Check
curl http://localhost:8000/health

# Members anzeigen
curl http://localhost:8000/api/v1/members/

# Sprint Availability Matrix
curl "http://localhost:8000/api/v1/sprints/1/availability"
```

## Architektur

- **Timezone**: Europe/Berlin
- **Sprache**: Deutsch
- **Scope**: Single Team mit Sprint-basierter Kapazitätsplanung
- **Features**: Availability-Grid mit Overrides, PTO-Management, Feiertagsberechnung nach Region

## Status & Nächste Schritte

### ✅ Abgeschlossen
- **Task 00**: Projektstruktur & Root-Dateien
- **Task 01**: FastAPI Skeleton + Settings + DB Session  
- **Task 02**: SQLAlchemy-Modelle + Alembic-Migration
- **Task 03**: Availability-Logik & REST-Endpunkte
- **Task 04**: Validierungen & Guards
- **Task 05**: Pytest Test Suite (60% Coverage, 25/25 Tests PASSED)
- **Task 06**: Docker Compose für MySQL + Backend ✅
- **Task 07**: Vue 3 Frontend Scaffold + PrimeVue + Pinia + Router ✅

### 🎯 Als Nächstes
- **Task 08**: Sprint-Flow UI (Draft → Active)
- **Task 09**: Availability Grid (Abhaken-Ansicht)

### 🚀 Quick Start mit Docker
```bash
# Komplettes Setup in 3 Schritten:
docker compose up -d
docker compose exec api alembic upgrade head  
docker compose exec api python seed.py

# API testen:
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/members/
```
