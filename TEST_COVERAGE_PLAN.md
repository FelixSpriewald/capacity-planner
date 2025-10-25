# Test Coverage Plan - 70% Target

## 🎯 Ziel: 70% Test Coverage für Frontend und Backend

## 📊 Aufgabenverteilung:

### **Phase 1: Status Quo Analyse (Tasks 1, 5)**

#### Backend Coverage Analyse
- [ ] Bestehende Tests inventarisieren
- [ ] pytest-cov Setup für Coverage-Reports
- [ ] Baseline-Coverage messen
- [ ] Kritische Bereiche ohne Tests identifizieren

#### Frontend Coverage Analyse
- [ ] Vitest Coverage Setup prüfen
- [ ] Bestehende Vue Component Tests finden
- [ ] @vue/test-utils Integration prüfen
- [ ] Baseline-Coverage messen

---

### **Phase 2: Backend Tests (Tasks 2-4)**

#### Core Services Tests (availability.py)
```python
# Priorität: HOCH - Business Logic
tests/services/test_availability.py
- test_calculate_working_days()
- test_calculate_holidays_by_region()  
- test_calculate_efficiency()
- test_member_sum_days_with_allocation()
- test_available_capacity_calculations()
```

#### API Endpoints Tests
```python
# Priorität: HOCH - User-facing APIs
tests/api/test_availability_endpoints.py
- test_get_sprint_availability_success()
- test_get_sprint_availability_not_found()
- test_patch_availability_override()
- test_error_handling_and_validation()
```

#### Database Layer Tests
```python
# Priorität: MITTEL - Data Layer
tests/models/test_models.py  
- test_sprint_model_crud()
- test_member_model_relationships()
- test_availability_override_constraints()
```

---

### **Phase 3: Frontend Tests (Tasks 6-8)**

#### Core Components Tests
```typescript
// Priorität: HOCH - User Interface
src/components/__tests__/
- AvailabilityDialog.spec.ts
- SprintInfoDashboard.spec.ts  
- MemberRow.spec.ts
- StatusLegend.spec.ts
```

#### Store/Services Tests
```typescript
// Priorität: HOCH - State Management
src/stores/__tests__/
- sprints.spec.ts
- members.spec.ts
src/services/__tests__/
- api.spec.ts
```

#### Utils/Helpers Tests  
```typescript
// Priorität: MITTEL - Utility Functions
src/utils/__tests__/
- date-utils.spec.ts
- validation.spec.ts
```

---

### **Phase 4: Integration & Optimization (Tasks 9-10)**

#### E2E Tests
```typescript
// Priorität: MITTEL - End-to-End Flows
e2e/
- sprint-management.spec.ts
- availability-editing.spec.ts
- dashboard-calculations.spec.ts
```

#### Coverage Optimization
- [ ] Coverage-Lücken schließen
- [ ] CI/CD Pipeline Setup
- [ ] Coverage-Reports automatisieren

---

## 🔧 **Technischer Setup:**

### Backend Testing Stack
```bash
# In capacity-be/
pip install pytest pytest-cov pytest-asyncio httpx
pytest --cov=app --cov-report=html tests/
```

### Frontend Testing Stack  
```bash
# In capacity-fe/
npm install --save-dev @vue/test-utils jsdom
npm run test:coverage
```

---

## 📈 **Coverage-Ziele pro Bereich:**

| Bereich | Target | Priorität |
|---------|--------|-----------|
| Backend Services | 85% | 🔴 Hoch |
| Backend API | 75% | 🔴 Hoch |
| Frontend Components | 70% | 🔴 Hoch |
| Frontend Stores | 80% | 🔴 Hoch |
| Backend Models | 60% | 🟡 Mittel |
| Frontend Utils | 90% | 🟡 Mittel |
| E2E Tests | 50% | 🟢 Niedrig |

**Gesamt-Target: 70%+ Combined Coverage**

---

## ⚡ **Empfohlene Reihenfolge:**

1. **Start**: Backend Coverage Analyse (Task 1)
2. **Core**: availability.py Service Tests (Task 2) 
3. **API**: REST Endpoints Tests (Task 3)
4. **Frontend**: Coverage Analyse (Task 5)
5. **Components**: Vue Component Tests (Task 6)
6. **Stores**: Pinia Store Tests (Task 7)
7. **Optimization**: Coverage auf 70%+ (Task 10)

**Geschätzte Zeit**: 3-4 Arbeitstage für 70% Coverage
**Kritischer Pfad**: Backend Services → API Tests → Frontend Components
