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

## Architektur

- **Timezone**: Europe/Berlin
- **Sprache**: Deutsch
- **Scope**: Single Team mit Sprint-basierter Kapazitätsplanung
- **Features**: Availability-Grid mit Overrides, PTO-Management, Feiertagsberechnung nach Region

## Nächste Schritte

1. Backend-Skeleton implementieren (`task 01_backend_skeleton`)
2. SQLAlchemy-Modelle erstellen (`task 02_backend_models_migrations`)
3. Frontend-Scaffold aufbauen (`task 07_frontend_scaffold`)
