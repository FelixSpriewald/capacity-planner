# Manual Testing Checklist - Capacity Planner

**Status**: 🟢 All services running (Frontend: http://localhost, API: http://localhost:8000, DB: MySQL)

## 🎯 Test Plan Overview
Diese manuelle Test-Checkliste hilft dabei, alle Features systematisch zu testen und fehlende Funktionalitäten zu identifizieren.

---

## 1. 📋 Basic System Health

### ✅ Infrastructure Tests
- [x] **Frontend erreichbar**: http://localhost → Sollte Vue App zeigen
- [x] **API Health Check**: http://localhost:8000/health → `{"status":"ok"}`
- [x] **API Docs**: http://localhost:8000/docs → Swagger UI sollte laden
- [x] **Database Connection**: API sollte ohne DB-Errors starten

### ✅ Navigation Tests
- [x] **Home Page**: http://localhost → Sollte Landing Page zeigen
- [x] **Members Page**: http://localhost/members → Navigation funktioniert
- [x] **Sprints Page**: http://localhost/sprints → Navigation funktioniert  
- [x] **Demo Page**: http://localhost/demo → Zeigt Task 12 Demo-Daten

---

## 2. 🎭 Demo Page Tests (Task 12 Verification)

**URL**: http://localhost/demo

### ✅ Demo Data Display
- [x] **Sprint Info**: Zeigt "Sprint W43" (20.10. - 31.10.2025)
- [x] **Team Members**: Alice Developer (DE-NW), Bogdan Coder (UA)
- [x] **Sprint Duration**: 2 Wochen, Mo-Fr Werktage sichtbar
- [x] **Weekends**: Sa/So als Weekend markiert
- [x] **Holidays**: 
  - [x] Reformationstag (31.10.) für Alice (DE-NW)
  - [x] Ukrainischer Feiertag (28.10.) für Bogdan (UA)
- [x] **PTO**: Alice hat PTO am 24.10.

### ✅ Availability Grid Functionality
- [ ] **Grid Rendering**: 2 Zeilen (Members) x 12 Spalten (Tage) sichtbar
- [ ] **Cell States**: Verschiedene Farben für available/unavailable/holiday/pto/weekend
- [ ] **Tooltips**: Hover über Zellen zeigt Details
- [ ] **Click Interaction**: Klick auf verfügbare Zelle ändert Status
- [ ] **Status Cycle**: available → half → unavailable → (zurück zu auto)

### ✅ Summary Calculations
- [ ] **Individual Sums**: Tage/Stunden pro Member korrekt
- [ ] **Team Total**: Gesamt-Kapazität stimmt (Alice: 7 Tage/56h, Bogdan: 8 Tage/64h)
- [ ] **Live Updates**: Summen ändern sich bei Grid-Interaktionen

---

## 3. 🔧 API Endpoints Testing

### ✅ Current API Status
Teste folgende Endpoints mit curl oder Postman:

```bash
# Health Check
curl http://localhost:8000/health

# Members (wahrscheinlich noch nicht implementiert)
curl http://localhost:8000/members

# Sprints (wahrscheinlich noch nicht implementiert)  
curl http://localhost:8000/sprints

# Verfügbare Endpoints checken
curl http://localhost:8000/docs
```

### 📝 Expected Missing Endpoints
- [ ] `GET /members` → 404 Not Found (noch nicht implementiert)
- [ ] `POST /members` → 404 Not Found
- [ ] `GET /sprints` → 404 Not Found
- [ ] `POST /sprints` → 404 Not Found
- [ ] `GET /sprints/{id}/availability` → 404 Not Found
- [ ] `PATCH /sprints/{id}/availability` → 404 Not Found

---

## 4. 🎨 Frontend Functionality Tests

### ✅ Members Management
**URL**: http://localhost/members

- [ ] **Page Load**: Zeigt Members-Verwaltung
- [ ] **Add Member**: Formular zum Hinzufügen neuer Members
- [ ] **Member List**: Zeigt aktuelle Members (falls vorhanden)
- [ ] **Edit Member**: Bearbeitung bestehender Members
- [ ] **Delete Member**: Entfernen von Members

### ✅ Sprint Management  
**URL**: http://localhost/sprints

- [ ] **Sprint List**: Zeigt verfügbare Sprints
- [ ] **Create Sprint**: Neuen Sprint anlegen
- [ ] **Sprint Status**: draft/active/closed Status-Management
- [ ] **Date Validation**: Start-/End-Datum Validierung
- [ ] **Sprint Copy**: Roster vom letzten Sprint kopieren

### ✅ Availability Grid (Hauptfeature)
**URL**: http://localhost/sprints/{id} (wenn Sprint-Detail existiert)

- [ ] **Sprint Selection**: Sprint auswählen und Grid laden
- [ ] **Member Roster**: Members zum Sprint hinzufügen/entfernen
- [ ] **PTO Management**: PTO für Members eintragen
- [ ] **Grid Interactions**: Cell-Click Status-Änderungen
- [ ] **Bulk Operations**: Spalten/Zeilen-weise Änderungen
- [ ] **Override System**: Auto-Status vs. Manual Override
- [ ] **Save Changes**: PATCH-Requests an API senden

---

## 5. 🧪 Component Testing

### ✅ AvailabilityGrid Component
- [ ] **Props Handling**: Korrekte Sprint/Member-Daten übergabe
- [ ] **Event Handling**: Cell-Click Events funktionieren
- [ ] **State Management**: Store-Integration funktioniert
- [ ] **Error Handling**: Graceful Loading/Error States

### ✅ Navigation Component
- [ ] **Route Highlighting**: Aktive Route hervorgehoben
- [ ] **Responsive Design**: Navigation auf verschiedenen Bildschirmgrößen

---

## 6. 🔍 Error Scenarios

### ✅ Network/API Errors
- [ ] **API Offline**: Was passiert wenn Backend down ist?
- [ ] **Slow API**: Loading States korrekt angezeigt?
- [ ] **404 Endpoints**: Graceful Fehlerbehandlung?
- [ ] **CORS Issues**: Cross-Origin Requests funktionieren?

### ✅ Data Validation
- [ ] **Invalid Dates**: Sprint mit End < Start Date
- [ ] **Missing Data**: Leere Members/Sprints
- [ ] **Concurrent Changes**: Mehrere User-Änderungen

---

## 7. 📱 Browser/Device Testing

### ✅ Cross-Browser
- [ ] **Chrome**: Funktioniert vollständig
- [ ] **Firefox**: Alle Features verfügbar
- [ ] **Safari**: Kompatibilität OK

### ✅ Responsive Design
- [ ] **Desktop**: 1920x1080+ optimiert
- [ ] **Tablet**: 768px-1024px brauchbar
- [ ] **Mobile**: 375px+ nutzbar

---

## 🚀 Priority Action Items

Nach diesem Test sollten wir diese Items priorisiert angehen:

### 🔴 Critical (Erst implementieren)
1. **Backend API Endpoints** - Alle REST-Endpoints aus project.json implementieren
2. **Database Models** - SQLAlchemy Models für alle Entities
3. **API-Frontend Integration** - Echte API-Calls statt Mock-Daten

### 🟡 High Priority (Danach)
1. **Sprint/Member Management UI** - Vollständige CRUD-Operationen
2. **Availability Grid Backend Logic** - Auto-Status Berechnung
3. **PTO/Holiday Management** - Vollständiges Management-Interface

### 🟢 Medium Priority (Später)
1. **Error Handling & Validation** - Robuste Fehlerbehandlung
2. **Performance Optimization** - Grid-Performance bei vielen Daten
3. **Advanced Features** - Bulk-Operations, Import/Export

---

## 📝 Test Execution

**Datum**: _____________  
**Tester**: _____________  
**Environment**: Docker Compose Production Setup  

### Completion Status:
- [ ] All Basic Tests Completed
- [ ] All Demo Tests Completed  
- [ ] API Status Documented
- [ ] Frontend Issues Identified
- [ ] Priority List Created

**Nächste Schritte**: ___________________________
