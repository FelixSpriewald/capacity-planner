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
        <Card class="sprint-card">
          <template #title>
            <div class="sprint-title-row">
              <span>{{ sprint.name }}</span>
              <Button
                icon="pi pi-pencil"
                class="p-button-text p-button-sm"
                @click="editSprint(sprint)"
                v-tooltip="'Sprint bearbeiten'"
              />
            </div>
          </template>
          <template #content>
            <div class="sprint-content">
              <div class="sprint-info">
                <div class="sprint-dates">
                  <span class="date-range">
                    {{ formatDateRange(sprint.start_date, sprint.end_date) }}
                  </span>
                  <Tag :value="getStatusLabel(sprint.status)" :severity="getStatusSeverity(sprint.status)" />
                </div>
                <div class="sprint-stats">
                  <div class="stat-item">
                    <i class="pi pi-users"></i>
                    <span>{{ sprint.member_count || 0 }} Teilnehmer</span>
                  </div>
                  <div class="stat-item">
                    <i class="pi pi-clock"></i>
                    <span>{{ sprint.total_capacity_hours || 0 }}h Kapazität</span>
                  </div>
                  <div class="stat-item">
                    <i class="pi pi-calendar"></i>
                    <span>{{ sprint.working_days || 0 }} Arbeitstage</span>
                  </div>
                </div>
                <div class="sprint-actions-bottom">
                  <Button
                    label="Team Roster"
                    icon="pi pi-users"
                    class="p-button-outlined p-button-sm"
                    @click="selectSprint(sprint); showRoster()"
                  />
                  <Button
                    label="Verfügbarkeit"
                    icon="pi pi-calendar"
                    class="p-button-outlined p-button-sm"
                    @click="selectSprint(sprint); showAvailability()"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>                <!-- Expandable Content -->
                <div v-if="expandedSprint === sprint.sprint_id" class="expanded-content">
                  <div class="content-tabs">
                    <Button
                      :label="'Team Roster'"
                      :class="{ 'p-button-outlined': activeTab !== 'roster' }"
                      @click="setActiveTab('roster')"
                      class="tab-button"
                    />
                    <Button
                      :label="'Availability Grid'"
                      :class="{ 'p-button-outlined': activeTab !== 'grid' }"
                      @click="setActiveTab('grid')"
                      class="tab-button"
                    />
                  </div>
                  
                  <!-- Team Roster Tab -->
                  <div v-if="activeTab === 'roster'" class="roster-content">
                    <div v-if="getRosterForSprint(sprint.sprint_id).length === 0" class="empty-roster">
                      <i class="pi pi-users"></i>
                      <p>Keine Team-Mitglieder zugewiesen</p>
                      <Button
                        label="Team bearbeiten"
                        icon="pi pi-plus"
                        @click="openRosterDialog(sprint)"
                        class="p-button-sm"
                      />
                    </div>
                    <div v-else class="roster-list">
                      <div class="roster-header">
                        <h5>Team-Mitglieder</h5>
                        <Button
                          icon="pi pi-pencil"
                          @click="openRosterDialog(sprint)"
                          class="p-button-text p-button-sm"
                          v-tooltip="'Team bearbeiten'"
                        />
                      </div>
                      <div class="roster-members">
                        <div 
                          v-for="member in getRosterForSprint(sprint.sprint_id)" 
                          :key="member.member_id" 
                          class="roster-member"
                        >
                          <div class="member-name">{{ getMemberName(member.member_id) }}</div>
                          <div class="member-details">
                            <span class="allocation">{{ Math.round(member.allocation * 100) }}%</span>
                            <span v-if="member.assignment_from || member.assignment_to" class="assignment">
                              {{ formatAssignmentPeriod(member.assignment_from, member.assignment_to) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Availability Grid Tab -->
                  <div v-if="activeTab === 'grid'" class="grid-content">
                    <div v-if="getAvailabilityLoading(sprint.sprint_id)" class="loading-content">
                      <ProgressSpinner size="30px" />
                      <span>Lade Availability...</span>
                    </div>
                    <div v-else-if="!getAvailabilityData(sprint.sprint_id)?.members?.length" class="empty-grid">
                      <i class="pi pi-table"></i>
                      <p>Keine Availability-Daten</p>
                      <Button
                        label="Availability laden"
                        @click="loadAvailabilityForSprint(sprint)"
                        class="p-button-sm"
                      />
                    </div>
                    <div v-else class="availability-grid-compact">
                      <!-- Compact Grid -->
                      <div class="grid-header">
                        <div class="grid-legend">
                          <div class="legend-item"><div class="dot available"></div>Verfügbar</div>
                          <div class="legend-item"><div class="dot half"></div>Halbtags</div>
                          <div class="legend-item"><div class="dot unavailable"></div>Nicht verfügbar</div>
                        </div>
                        <Button
                          label="Vollbild"
                          icon="pi pi-expand"
                          @click="openFullGrid(sprint)"
                          class="p-button-text p-button-sm"
                        />
                      </div>
                      <div class="compact-grid">
                        <div v-for="member in getAvailabilityData(sprint.sprint_id)?.members.slice(0, 3)" :key="member.member_id" class="member-row-compact">
                          <div class="member-name-compact">{{ member.member_name }}</div>
                          <div class="days-compact">
                            <div 
                              v-for="(status, dayIndex) in member.availability.slice(0, 10)" 
                              :key="dayIndex"
                              class="day-compact"
                              :class="{
                                'available': status === 2,
                                'partially-available': status === 1,
                                'unavailable': status === 0
                              }"
                            ></div>
                          </div>
                        </div>
                        <div v-if="getAvailabilityData(sprint.sprint_id) && getAvailabilityData(sprint.sprint_id)!.members.length > 3" class="more-members">
                          +{{ getAvailabilityData(sprint.sprint_id)!.members.length - 3 }} weitere...
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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

    <!-- Availability Grid Dialog -->
    <Dialog
      v-model:visible="showAvailabilityDialog"
      modal
      :header="`Availability Grid - ${selectedSprint?.name || 'Sprint'}`"
      :style="{ width: '90vw', height: '80vh' }"
      :maximizable="true"
      :closable="true"
    >
      <div class="simple-availability-grid">
        <div v-if="availabilityLoading" class="loading-state">
          <ProgressSpinner size="50px" />
          <p>Lade Availability Daten...</p>
        </div>

        <div v-else-if="!selectedSprint" class="empty-state">
          <i class="pi pi-calendar-times empty-icon"></i>
          <h3>Kein Sprint ausgewählt</h3>
          <p>Bitte wählen Sie einen Sprint aus</p>
        </div>

        <div v-else-if="!sprintsStore.availability || !sprintsStore.availability.members?.length" class="empty-state">
          <i class="pi pi-users empty-icon"></i>
          <h3>Keine Team-Mitglieder</h3>
          <p>Fügen Sie Team-Mitglieder zu diesem Sprint hinzu</p>
        </div>

        <div v-else class="grid-content">
          <!-- Legend -->
          <div class="legend-bar">
            <div class="legend-item">
              <div class="status-dot available"></div>
              <span>Verfügbar</span>
            </div>
            <div class="legend-item">
              <div class="status-dot half-available"></div>
              <span>Halbtags</span>
            </div>
            <div class="legend-item">
              <div class="status-dot unavailable"></div>
              <span>Nicht verfügbar</span>
            </div>
            <div class="legend-item">
              <div class="status-dot outside"></div>
              <span>Außerhalb Assignment</span>
            </div>
            <div class="legend-item">
              <i class="pi pi-hand-pointer" style="color: #3b82f6; margin-right: 4px;"></i>
              <span>Klicken zum Bearbeiten</span>
            </div>
          </div>

          <!-- Grid Table -->
          <div class="grid-table-container">
            <table class="availability-table">
              <thead>
                <tr>
                  <th class="member-column">Team Member</th>
                  <th v-for="day in availabilityDays" :key="day.date" class="day-column" :class="{ 'after-weekend': day.isAfterWeekend }">
                    <div class="day-header">
                      <div class="day-name">{{ day.dayName }}</div>
                      <div class="day-date">{{ day.dayDate }}</div>
                    </div>
                  </th>
                  <th class="summary-column">Gesamt</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="member in sprintsStore.availability.members" :key="member.member_id" class="member-row">
                  <td class="member-cell">
                    <div class="member-info">
                      <div class="member-name">{{ (member as any).name || member.member_name }}</div>
                      <div class="member-allocation">{{ Math.round(parseFloat((member as any).allocation || '1') * 100) }}%</div>
                    </div>
                  </td>
                  <td v-for="day in member.days.filter(d => !isWeekendDay((d as any).date))" :key="(day as any).date" class="day-cell" :class="{ 'after-weekend': isAfterWeekend((day as any).date) }">
                    <div
                      class="availability-status editable"
                      :class="getAvailabilityClass(day)"
                      :title="getAvailabilityTooltip(day, (member as any).name || member.member_name)"
                      @click="toggleAvailability(member.member_id, (day as any).date, day)"
                    >
                    </div>
                  </td>
                  <td class="summary-cell">
                    <div class="member-summary">
                      <div class="hours">{{ ((member as any).sum_hours)?.toFixed(1) || 0 }}h</div>
                      <div class="days">{{ (member as any).sum_days || 0 }} Tage</div>
                    </div>
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="total-row">
                  <td><strong>Team Gesamt</strong></td>
                  <td v-for="day in availabilityDays" :key="`total-${day.date}`" class="day-total" :class="{ 'after-weekend': day.isAfterWeekend }">
                    <strong>{{ getDayTotal(day.date || '') }}h</strong>
                  </td>
                  <td class="total-summary">
                    <div class="team-total">
                      <div class="hours"><strong>{{ ((sprintsStore.availability as any).sum_hours_team)?.toFixed(1) || 0 }}h</strong></div>
                      <div class="days">{{ (sprintsStore.availability as any).sum_days_team || 0 }} Tage</div>
                    </div>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
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
const showAvailabilityDialog = ref(false)
const availabilityLoading = ref(false)
const editingSprint = ref<Sprint | null>(null)

const formLoading = ref(false)

// Computed properties
const availabilityDays = computed(() => {
  if (!selectedSprint.value) return []

  const days = []
  const startDate = new Date(selectedSprint.value.start_date)
  const endDate = new Date(selectedSprint.value.end_date)

  for (let date = new Date(startDate); date <= endDate; date.setDate(date.getDate() + 1)) {
    const dayOfWeek = date.getDay()
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6

    // Skip weekends
    if (!isWeekend) {
      days.push({
        date: date.toISOString().split('T')[0],
        dayName: date.toLocaleDateString('de-DE', { weekday: 'short' }),
        dayDate: date.toLocaleDateString('de-DE', { day: 'numeric', month: 'numeric' }),
        isWeekend,
        isAfterWeekend: dayOfWeek === 1 // Monday
      })
    }
  }

  return days
})

const createSprint = () => {
  editingSprint.value = null
  showSprintForm.value = true
}

const selectSprint = (sprint: Sprint) => {
  selectedSprint.value = sprint
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

const showAvailability = async () => {
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
    availabilityLoading.value = true
    await sprintsStore.fetchAvailability(selectedSprint.value.sprint_id)
    showAvailabilityDialog.value = true
  } catch (err) {
    console.error('Error loading availability:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Availability Daten konnten nicht geladen werden',
      life: 3000
    })
  } finally {
    availabilityLoading.value = false
  }
}



const getAvailabilityClass = (day: Record<string, unknown>) => {
  const classes = ['status-indicator']

  if (!day.in_assignment) {
    classes.push('outside-assignment')
  } else if (day.final_state === 'available') {
    classes.push('available')
  } else if (day.final_state === 'half') {
    classes.push('half-available')
  } else if (day.final_state === 'unavailable') {
    if (day.is_weekend) {
      classes.push('weekend')
    } else {
      classes.push('unavailable')
    }
  } else {
    classes.push('unavailable')
  }

  return classes.join(' ')
}

const getAvailabilityTooltip = (day: Record<string, unknown>, memberName: string) => {
  const dayDate = day.date
  let tooltip = `${memberName} - ${dayDate}\n`
  tooltip += `Status: ${day.final_state}\n`

  if (day.auto_state !== day.final_state) {
    tooltip += `Auto: ${day.auto_state}\n`
  }

  if (day.override_state) {
    tooltip += `Override: ${day.override_state}\n`
  }

  if (!day.in_assignment) {
    tooltip += 'Außerhalb des Assignments'
  }

  return tooltip
}

const isWeekendDay = (dateString: string) => {
  const date = new Date(dateString)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 0 || dayOfWeek === 6
}

const isAfterWeekend = (dateString: string) => {
  const date = new Date(dateString)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 1 // Monday
}

const getDayTotal = (date: string) => {
  if (!sprintsStore.availability?.members) return 0

  let totalHours = 0
  for (const member of sprintsStore.availability.members) {
    const dayData = member.days.find((d) => {
      const dayRecord = d as Record<string, unknown>
      return dayRecord.date === date
    })
    if (dayData && dayData.final_state === 'available') {
      // Use API field names
      const memberData = member as Record<string, unknown>
      const allocation = parseFloat(String(memberData.allocation || '1'))
      const employmentRatio = parseFloat(String(memberData.employment_ratio || '1'))
      totalHours += 8 * allocation * employmentRatio
    }
  }

  return Math.round(totalHours * 10) / 10
}

const toggleAvailability = async (memberId: number, date: string, currentDay: Record<string, unknown>) => {
  if (!selectedSprint.value) return

  // Determine next state based on current state
  let newState: 'available' | 'half' | 'unavailable'
  const currentState = currentDay.final_state as string

  // Cycle through states: available -> half -> unavailable -> available
  if (currentState === 'available') {
    newState = 'half'
  } else if (currentState === 'half') {
    newState = 'unavailable'
  } else {
    newState = 'available'
  }

  try {
    await sprintsStore.updateAvailabilityOverride(
      selectedSprint.value!.sprint_id,
      memberId,
      date,
      newState,
      'Geändert über Availability Grid'
    )

  } catch (error) {
    console.error('Error toggling availability:', error)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Verfügbarkeit konnte nicht geändert werden',
      life: 3000
    })
  }
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

const formatCapacityHours = (hours: number) => {
  if (hours === 0) return '0h'
  if (hours < 8) return `${hours.toFixed(1)}h`
  const days = Math.floor(hours / 8)
  const remainingHours = hours % 8
  if (remainingHours === 0) return `${days}d`
  return `${days}d ${remainingHours.toFixed(1)}h`
}

// Sprint expansion functions
const toggleSprintExpansion = async (sprint: Sprint) => {
  if (expandedSprint.value === sprint.sprint_id) {
    expandedSprint.value = null
  } else {
    expandedSprint.value = sprint.sprint_id
    sprintsStore.selectSprint(sprint)
    // Load roster and availability data
    await loadRosterForSprint(sprint)
    if (activeTab.value === 'grid') {
      await loadAvailabilityForSprint(sprint)
    }
  }
}

const setActiveTab = async (tab: 'roster' | 'grid') => {
  activeTab.value = tab
  if (tab === 'grid' && selectedSprint.value) {
    await loadAvailabilityForSprint(selectedSprint.value)
  }
}

// Roster helper functions
const getRosterForSprint = (sprintId: number) => {
  return roster.value.filter(r => r.sprint_id === sprintId)
}

const getMemberName = (memberId: number) => {
  const member = members.value.find(m => m.member_id === memberId)
  return member?.name || `Member ${memberId}`
}

const formatAssignmentPeriod = (from: string | null | undefined, to: string | null | undefined) => {
  if (!from && !to) return ''
  if (from && to) return `${new Date(from).toLocaleDateString('de-DE')} - ${new Date(to).toLocaleDateString('de-DE')}`
  if (from) return `ab ${new Date(from).toLocaleDateString('de-DE')}`
  if (to) return `bis ${new Date(to).toLocaleDateString('de-DE')}`
  return ''
}

const openRosterDialog = async (sprint: Sprint) => {
  sprintsStore.selectSprint(sprint)
  await loadRosterForSprint(sprint)
  showRosterDialog.value = true
}

const loadRosterForSprint = async (sprint: Sprint) => {
  try {
    await sprintsStore.fetchRoster(sprint.sprint_id)
  } catch (error) {
    console.error('Failed to load roster:', error)
  }
}

// Availability helper functions
const getAvailabilityData = (sprintId: number): AvailabilityData | undefined => {
  return availabilityData.value.get(sprintId)
}

const getAvailabilityLoading = (sprintId: number) => {
  return availabilityLoadingMap.value.get(sprintId) || false
}

const loadAvailabilityForSprint = async (sprint: Sprint) => {
  if (availabilityData.value.has(sprint.sprint_id)) return
  
  availabilityLoadingMap.value.set(sprint.sprint_id, true)
  try {
    const data = await sprintsStore.fetchAvailability(sprint.sprint_id)
    // Transform data to match interface
    const transformedData: AvailabilityData = {
      members: (data.members || []).map(member => ({
        member_id: member.member_id,
        member_name: member.member_name,
        assignment_from: null,
        assignment_to: null,
        availability: member.days ? member.days.map(d => {
          if (d.final_state === 'available') return 2
          if (d.final_state === 'half') return 1
          return 0
        }) : []
      })),
      work_days: []
    }
    availabilityData.value.set(sprint.sprint_id, transformedData)
  } catch (error) {
    console.error('Failed to load availability:', error)
  } finally {
    availabilityLoadingMap.value.set(sprint.sprint_id, false)
  }
}

const openFullGrid = async (sprint: Sprint) => {
  sprintsStore.selectSprint(sprint)
  await loadAvailabilityForSprint(sprint)
  showAvailabilityDialog.value = true
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

.sprint-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.875rem;
}

.stat-item i {
  color: #3498db;
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

/* Availability Grid Styles */
.grid-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.grid-legend {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.legend-bar {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.status-dot.available {
  background-color: #10b981;
}

.status-dot.half-available {
  background-color: #f59e0b;
}

.status-dot.unavailable {
  background-color: #ef4444;
}



.status-dot.outside {
  background-color: #6b7280;
}

.grid-table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.availability-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 0.875rem;
}

.availability-table th,
.availability-table td {
  padding: 0;
  border: 1px solid #e5e7eb;
  text-align: center;
  vertical-align: middle;
}

.member-column {
  min-width: 180px;
  background: #f9fafb;
  font-weight: 600;
  position: sticky;
  left: 0;
  z-index: 2;
}

.day-column {
  width: 40px;
  min-width: 40px;
  background: #f9fafb;
  font-weight: 500;
}

.day-column.after-weekend {
  border-left: 3px double #3b82f6;
}

.day-cell.after-weekend {
  border-left: 3px double #3b82f6;
}

.day-total.after-weekend {
  border-left: 3px double #3b82f6;
}



.summary-column {
  min-width: 80px;
  background: #f9fafb;
  font-weight: 600;
  position: sticky;
  right: 0;
  z-index: 2;
}

.day-header {
  padding: 0.5rem 0.25rem;
  line-height: 1.2;
}

.day-name {
  font-weight: 600;
  color: #374151;
}

.day-date {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 2px;
}

.member-row:nth-child(even) {
  background: #f9fafb;
}

.member-cell {
  padding: 1rem;
  text-align: left;
  background: white;
  position: sticky;
  left: 0;
  z-index: 1;
}

.member-row:nth-child(even) .member-cell {
  background: #f9fafb;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.member-name {
  font-weight: 600;
  color: #111827;
}

.member-allocation {
  font-size: 0.75rem;
  color: #6b7280;
}

.day-cell {
  width: 40px;
  height: 40px;
  padding: 2px;
}

.availability-status {
  width: 100%;
  height: 100%;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.2s ease;
}

.availability-status.editable {
  cursor: pointer;
}

.availability-status.editable:hover {
  transform: scale(1.1);
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid #3b82f6;
}

.availability-status.available {
  background-color: #10b981;
}

.availability-status.half-available {
  background-color: #f59e0b;
}

.availability-status.unavailable {
  background-color: #ef4444;
}



.availability-status.outside-assignment {
  background-color: #6b7280;
}



.summary-cell {
  padding: 1rem;
  background: white;
  position: sticky;
  right: 0;
  z-index: 1;
}

.member-row:nth-child(even) .summary-cell {
  background: #f9fafb;
}

.member-summary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: center;
}

.hours {
  font-weight: 600;
  color: #059669;
}

.days {
  font-size: 0.75rem;
  color: #6b7280;
}

.team-totals-row {
  background: #f3f4f6 !important;
  font-weight: 600;
}

.team-totals-row td {
  background: #f3f4f6 !important;
  border-top: 2px solid #d1d5db;
}

.day-total {
  font-weight: 600;
  color: #1f2937;
  padding: 0.5rem 0.25rem;
}

@media (max-width: 1024px) {
  .grid-legend {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .legend-item {
    font-size: 0.75rem;
  }
}

.availability-dialog-content {
  height: calc(90vh - 120px);
  overflow: auto;
  padding: 0;
}
</style>
