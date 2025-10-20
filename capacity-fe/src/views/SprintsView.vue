<template>
  <div class="sprints-view">
    <div class="page-header">
      <h1 class="page-title">
        <i class="pi pi-calendar"></i>
        Sprint Management
      </h1>
      <Button
        label="Neuer Sprint"
        icon="pi pi-plus"
        @click="createSprint"
        class="p-button-success"
      />
    </div>

    <div class="content-grid">
      <!-- Sprint Liste -->
      <div class="sprint-list">
        <Card>
          <template #title>Aktuelle Sprints</template>
          <template #content>
            <div v-if="loading" class="loading-state">
              <ProgressSpinner size="50px" />
              <p>Lade Sprints...</p>
            </div>

            <div v-else-if="sprints.length === 0" class="empty-state">
              <i class="pi pi-calendar-plus empty-icon"></i>
              <h3>Keine Sprints vorhanden</h3>
              <p>Erstelle deinen ersten Sprint um zu beginnen</p>
              <Button
                label="Sprint erstellen"
                icon="pi pi-plus"
                @click="createSprint"
                class="p-button-outlined"
              />
            </div>

            <div v-else class="sprint-cards">
              <div
                v-for="sprint in sprints"
                :key="sprint.sprint_id"
                class="sprint-card"
                @click="selectSprint(sprint)"
              >
                <div class="sprint-header">
                  <h4>{{ sprint.name }}</h4>
                  <Tag :value="sprint.status" :severity="getStatusSeverity(sprint.status)" />
                </div>
                <div class="sprint-dates">
                  <i class="pi pi-calendar"></i>
                  <span>{{ formatDateRange(sprint.start_date, sprint.end_date) }}</span>
                </div>
                <div class="sprint-actions">
                  <Button
                    icon="pi pi-eye"
                    class="p-button-text p-button-sm"
                    @click.stop="viewSprint(sprint)"
                    v-tooltip="'Sprint anzeigen'"
                  />
                  <Button
                    icon="pi pi-pencil"
                    class="p-button-text p-button-sm"
                    @click.stop="editSprint(sprint)"
                    v-tooltip="'Sprint bearbeiten'"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Sprint Details -->
      <div class="sprint-details" v-if="selectedSprint">
        <Card>
          <template #title>{{ selectedSprint.name }}</template>
          <template #content>
            <div class="details-content">
              <div class="detail-row">
                <strong>Status:</strong>
                <Tag
                  :value="selectedSprint.status"
                  :severity="getStatusSeverity(selectedSprint.status)"
                />
              </div>
              <div class="detail-row">
                <strong>Zeitraum:</strong>
                <span>{{
                  formatDateRange(selectedSprint.start_date, selectedSprint.end_date)
                }}</span>
              </div>
              <div class="detail-row">
                <strong>Arbeitstage:</strong>
                <span
                  >{{
                    calculateWorkingDays(selectedSprint.start_date, selectedSprint.end_date)
                  }}
                  Tage</span
                >
              </div>
            </div>

            <div class="action-buttons">
              <Button
                label="Availability Grid"
                icon="pi pi-table"
                @click="showAvailability"
                class="p-button-primary"
              />
              <Button
                label="Team Roster"
                icon="pi pi-users"
                @click="showRoster"
                class="p-button-outlined"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

interface Sprint {
  sprint_id: number
  name: string
  start_date: string
  end_date: string
  status: 'draft' | 'active' | 'completed'
}

const loading = ref(true)
const sprints = ref<Sprint[]>([])
const selectedSprint = ref<Sprint | null>(null)

const createSprint = () => {
  console.log('Neuer Sprint erstellen...')
}

const selectSprint = (sprint: Sprint) => {
  selectedSprint.value = sprint
}

const viewSprint = (sprint: Sprint) => {
  console.log('Sprint anzeigen:', sprint.name)
}

const editSprint = (sprint: Sprint) => {
  console.log('Sprint bearbeiten:', sprint.name)
}

const showAvailability = () => {
  console.log('Availability Grid anzeigen für Sprint:', selectedSprint.value?.name)
}

const showRoster = () => {
  console.log('Team Roster anzeigen für Sprint:', selectedSprint.value?.name)
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'draft':
      return 'secondary'
    case 'active':
      return 'success'
    case 'completed':
      return 'info'
    default:
      return 'secondary'
  }
}

const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate).toLocaleDateString('de-DE')
  const end = new Date(endDate).toLocaleDateString('de-DE')
  return `${start} - ${end}`
}

const calculateWorkingDays = (startDate: string, endDate: string) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  // Grobe Schätzung ohne Feiertage
  const weekDays = Math.floor((diffDays * 5) / 7)
  return weekDays
}

onMounted(async () => {
  // Simuliere API-Call
  setTimeout(() => {
    sprints.value = [
      {
        sprint_id: 1,
        name: 'Sprint W43-44 2025',
        start_date: '2025-10-21',
        end_date: '2025-11-01',
        status: 'draft',
      },
    ]
    loading.value = false

    // Auto-select first sprint
    if (sprints.value.length > 0) {
      selectedSprint.value = sprints.value[0]!
    }
  }, 1000)
})
</script>

<style scoped>
.sprints-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #95a5a6;
  margin-bottom: 2rem;
}

.sprint-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sprint-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.sprint-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.1);
  transform: translateY(-1px);
}

.sprint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sprint-header h4 {
  margin: 0;
  color: #2c3e50;
}

.sprint-dates {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.sprint-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.details-content {
  margin-bottom: 2rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.detail-row:last-child {
  border-bottom: none;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-buttons .p-button {
  flex: 1;
  min-width: 150px;
}
</style>
