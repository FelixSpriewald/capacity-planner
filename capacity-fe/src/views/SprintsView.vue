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
                    icon="pi pi-pencil"
                    class="p-button-text p-button-sm"
                    @click.stop="editSprint(sprint)"
                    v-tooltip="'Sprint bearbeiten'"
                  />
                  <Button
                    icon="pi pi-trash"
                    class="p-button-text p-button-sm p-button-danger"
                    @click.stop="confirmDeleteSprint(sprint)"
                    v-tooltip="'Sprint löschen'"
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

    <!-- Sprint Form Dialog -->
    <SprintForm
      v-model:visible="showSprintForm"
      :sprint="editingSprint"
      :loading="formLoading"
      @submit="handleSprintSubmit"
    />

    <!-- Team Roster Dialog -->
    <TeamRosterDialog
      v-model:visible="showRosterDialog"
      :sprint="selectedSprint"
      :roster="roster"
      :members="members"
      :loading="rosterLoading"
      @add-member="handleAddMember"
      @update-member="handleUpdateMember"
      @remove-member="handleRemoveMember"
    />

    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useSprintsStore } from '@/stores/sprints'
import { useMembersStore } from '@/stores/members'
import SprintForm from '@/components/forms/SprintForm.vue'
import TeamRosterDialog from '@/components/dialogs/TeamRosterDialog.vue'
import type { Sprint, SprintStatus } from '@/types'

// Store und Services
const sprintsStore = useSprintsStore()
const membersStore = useMembersStore()
const toast = useToast()
const confirm = useConfirm()

// Reactive state
const { sprints, selectedSprint, loading, roster, rosterLoading } = storeToRefs(sprintsStore)
const { members } = storeToRefs(membersStore)
const showSprintForm = ref(false)
const showRosterDialog = ref(false)
const editingSprint = ref<Sprint | null>(null)
const formLoading = ref(false)

const createSprint = () => {
  editingSprint.value = null
  showSprintForm.value = true
}

const selectSprint = (sprint: Sprint) => {
  // Select the sprint to show details
  sprintsStore.selectSprint(sprint)

  // Scroll to sprint details with smooth animation
  const detailsElement = document.querySelector('.sprint-details')
  if (detailsElement) {
    detailsElement.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }

  // Show success toast
  toast.add({
    severity: 'info',
    summary: 'Sprint Details',
    detail: `Zeige Details für "${sprint.name}"`,
    life: 2000
  })
}

// Types
interface SprintFormData {
  name: string
  start_date: string
  end_date: string
  status?: SprintStatus
}

const handleSprintSubmit = async (formData: SprintFormData) => {
  try {
    formLoading.value = true

    if (editingSprint.value) {
      // Update existing sprint
      console.log('Updating sprint:', editingSprint.value.sprint_id, 'with data:', formData)
      const updatedSprint = await sprintsStore.updateSprint(editingSprint.value.sprint_id, formData)
      console.log('Sprint updated successfully:', updatedSprint)

      // Refresh the sprint list to ensure UI is in sync
      await sprintsStore.fetchSprints()

      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Sprint wurde erfolgreich aktualisiert',
        life: 3000
      })
    } else {
      // Create new sprint - ensure status is set
      const sprintData = {
        ...formData,
        status: (formData.status || 'draft') as SprintStatus
      }
      console.log('Creating new sprint with data:', sprintData)
      const newSprint = await sprintsStore.createSprint(sprintData)
      console.log('Sprint created successfully:', newSprint)

      // Refresh the sprint list to ensure UI is in sync
      await sprintsStore.fetchSprints()

      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: `Sprint "${newSprint.name}" wurde erfolgreich erstellt`,
        life: 3000
      })
    }

    showSprintForm.value = false
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err instanceof Error ? err.message : 'Fehler beim Speichern des Sprints',
      life: 5000
    })
  } finally {
    formLoading.value = false
  }
}



const editSprint = (sprint: Sprint) => {
  editingSprint.value = sprint
  showSprintForm.value = true
}

const confirmDeleteSprint = (sprint: Sprint) => {
  confirm.require({
    message: `Möchten Sie den Sprint "${sprint.name}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`,
    header: 'Sprint löschen',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    rejectLabel: 'Abbrechen',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Löschen',
    accept: () => {
      deleteSprint(sprint)
    }
  })
}

const deleteSprint = async (sprint: Sprint) => {
  try {
    await sprintsStore.deleteSprint(sprint.sprint_id)

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: `Sprint "${sprint.name}" wurde erfolgreich gelöscht`,
      life: 3000
    })

    // Refresh sprint list
    await sprintsStore.fetchSprints()

    // Auto-select first sprint if available
    if (sprints.value.length > 0) {
      sprintsStore.selectSprint(sprints.value[0]!)
    }
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err instanceof Error ? err.message : 'Fehler beim Löschen des Sprints',
      life: 5000
    })
  }
}

// Roster Event Handlers
const handleAddMember = async (memberData: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }) => {
  if (!selectedSprint.value) return

  try {
    await sprintsStore.addMemberToRoster(selectedSprint.value.sprint_id, memberData)

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Member wurde erfolgreich hinzugefügt',
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err instanceof Error ? err.message : 'Fehler beim Hinzufügen des Members',
      life: 5000
    })
  }
}

const handleUpdateMember = async (memberData: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }) => {
  if (!selectedSprint.value) return

  try {
    await sprintsStore.updateRosterMember(selectedSprint.value.sprint_id, memberData)

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Member wurde erfolgreich aktualisiert',
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err instanceof Error ? err.message : 'Fehler beim Aktualisieren des Members',
      life: 5000
    })
  }
}

const handleRemoveMember = async (memberId: number) => {
  if (!selectedSprint.value || rosterLoading.value) return

  try {
    await sprintsStore.removeMemberFromRoster(selectedSprint.value.sprint_id, memberId)

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Member wurde erfolgreich entfernt',
      life: 3000
    })
  } catch (error) {
    console.error('Failed to remove member:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error instanceof Error ? error.message : 'Fehler beim Entfernen des Members',
      life: 5000
    })
  }
}

const showAvailability = () => {
  console.log('Availability Grid anzeigen für Sprint:', selectedSprint.value?.name)
}

const showRoster = async () => {
  if (!selectedSprint.value) {
    toast.add({
      severity: 'warn',
      summary: 'Kein Sprint ausgewählt',
      detail: 'Bitte wählen Sie zuerst einen Sprint aus',
      life: 3000
    })
    return
  }

  try {
    // Load members and roster data
    await Promise.all([
      membersStore.fetchMembers(),
      sprintsStore.fetchRoster(selectedSprint.value.sprint_id)
    ])

    showRosterDialog.value = true
  } catch (error) {
    console.error('Failed to load roster data:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Laden der Roster-Daten',
      life: 5000
    })
  }
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

// Load sprints on mount
onMounted(async () => {
  try {
    console.log('SprintsView: Loading sprints on mount...')
    await sprintsStore.fetchSprints()

    // Auto-select first sprint
    if (sprints.value.length > 0) {
      sprintsStore.selectSprint(sprints.value[0]!)
    }
    console.log('SprintsView: Sprints loaded successfully:', sprints.value)
  } catch (err) {
    console.error('SprintsView: Failed to load sprints:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Laden der Sprints',
      life: 5000
    })
  }
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
