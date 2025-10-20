<template>
  <div class="availability-grid">
    <div class="grid-header">
      <h3 class="grid-title">
        <i class="pi pi-calendar-clock"></i>
        Availability Grid
        <span v-if="sprint" class="sprint-name"> - {{ sprint.name }}</span>
      </h3>

      <div class="grid-controls">
        <div class="legend">
          <div class="legend-item">
            <div class="status-cell available"></div>
            <span>Available</span>
          </div>
          <div class="legend-item">
            <div class="status-cell out"></div>
            <span>Out</span>
          </div>
          <div class="legend-item">
            <div class="status-cell half"></div>
            <span>Half Day</span>
          </div>
          <div class="legend-item">
            <div class="status-cell weekend"></div>
            <span>Weekend</span>
          </div>
          <div class="legend-item">
            <div class="status-cell holiday"></div>
            <span>Holiday</span>
          </div>
          <div class="legend-item">
            <div class="status-cell pto"></div>
            <span>PTO</span>
          </div>
        </div>

        <Button
          label="Refresh"
          icon="pi pi-refresh"
          @click="refreshData"
          :loading="loading"
          size="small"
        />
      </div>
    </div>

    <!-- Bulk Actions Toolbar -->
    <div v-if="selectionMode" class="bulk-actions-toolbar">
      <div class="selection-info">
        <span class="selection-count">{{ selectedCells.size }} cells selected</span>
        <Button
          label="Clear Selection"
          icon="pi pi-times"
          @click="clearSelection"
          size="small"
          severity="secondary"
        />
      </div>

      <div class="bulk-actions">
        <span class="bulk-label">Set selected to:</span>
        <Button
          label="Available"
          icon="pi pi-check"
          @click="setBulkState('available')"
          size="small"
          severity="success"
          :disabled="selectedCells.size === 0"
        />
        <Button
          label="Half Day"
          icon="pi pi-clock"
          @click="setBulkState('half')"
          size="small"
          severity="warning"
          :disabled="selectedCells.size === 0"
        />
        <Button
          label="Out"
          icon="pi pi-times"
          @click="setBulkState('out')"
          size="small"
          severity="danger"
          :disabled="selectedCells.size === 0"
        />
        <Button
          label="Clear Override"
          icon="pi pi-undo"
          @click="setBulkState(null)"
          size="small"
          severity="secondary"
          :disabled="selectedCells.size === 0"
        />
      </div>

      <div class="selection-mode-controls">
        <Button
          label="Exit Selection"
          icon="pi pi-times"
          @click="exitSelectionMode"
          size="small"
          severity="secondary"
        />
      </div>
    </div>

    <!-- Grid Controls -->
    <div class="grid-controls-bar">
      <div class="quick-actions">
        <Button
          label="Select Mode"
          icon="pi pi-check-square"
          @click="enterSelectionMode"
          size="small"
          :severity="selectionMode ? 'success' : 'secondary'"
        />
        <Button
          label="Select Column"
          icon="pi pi-table"
          @click="selectColumn"
          size="small"
          :disabled="!hoveredColumn"
        />
        <Button
          label="Select All"
          icon="pi pi-check-square"
          @click="selectAll"
          size="small"
        />
        <Button
          label="Select Weekends"
          icon="pi pi-calendar"
          @click="selectWeekends"
          size="small"
        />
      </div>

      <div class="keyboard-hint">
        <small>
          💡 Hold <kbd>Shift</kbd> to select multiple cells | <kbd>Ctrl/Cmd</kbd> + click for column/row
        </small>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner size="50px" />
      <p>Loading availability data...</p>
    </div>

    <div v-else-if="!sprint" class="empty-state">
      <i class="pi pi-calendar-times empty-icon"></i>
      <h3>No Sprint Selected</h3>
      <p>Please select a sprint to view the availability grid</p>
    </div>

    <div v-else-if="!availability || availability.members.length === 0" class="empty-state">
      <i class="pi pi-users empty-icon"></i>
      <h3>No Team Members</h3>
      <p>Add team members to see their availability</p>
    </div>

    <div v-else class="grid-container">
      <!-- Grid Table -->
      <div class="grid-table">
        <!-- Header Row -->
        <div class="grid-row header-row">
          <div class="member-column header-cell">
            <strong>Team Member</strong>
          </div>
          <div
            v-for="day in sprintDays"
            :key="day.date"
            class="day-column header-cell"
            :class="{ 'weekend-header': day.isWeekend }"
          >
            <div class="day-header">
              <div class="day-name">{{ day.dayName }}</div>
              <div class="day-date">{{ day.displayDate }}</div>
            </div>
          </div>
          <div class="summary-column header-cell">
            <strong>Summary</strong>
          </div>
        </div>

        <!-- Member Rows -->
        <div
          v-for="memberAvailability in availability.members"
          :key="memberAvailability.member_id"
          class="grid-row member-row"
        >
          <!-- Member Info -->
          <div class="member-column member-cell">
            <div class="member-info">
              <div class="member-name">{{ memberAvailability.member_name }}</div>
              <div class="member-ratio">
                {{ formatEmploymentRatio(getMemberRatio(memberAvailability.member_id)) }}
              </div>
            </div>
          </div>

          <!-- Day Cells -->
          <div
            v-for="dayAvailability in memberAvailability.days"
            :key="dayAvailability.day"
            class="day-column day-cell"
            :class="getDayCellClass(dayAvailability)"
            @click="handleCellClick(memberAvailability.member_id, dayAvailability.day, dayAvailability)"
            @mouseenter="hoveredColumn = dayAvailability.day; hoveredRow = memberAvailability.member_id"
            @mouseleave="hoveredColumn = null; hoveredRow = null"
            :title="getDayCellTooltip(dayAvailability, memberAvailability.member_id)"
          >
            <div class="cell-content">
              <div class="status-indicator"></div>
              <div v-if="dayAvailability.override_state" class="override-indicator">
                <i class="pi pi-pencil"></i>
              </div>
              <div v-if="getWarningType(dayAvailability)" class="warning-indicator">
                <i                 :class="getWarningIcon(dayAvailability)">></i>
              </div>
              <div v-if="selectionMode && isSelected(memberAvailability.member_id, dayAvailability.day)" class="selection-indicator">
                <i class="pi pi-check"></i>
              </div>
            </div>
          </div>

          <!-- Summary Cell -->
          <div class="summary-column summary-cell">
            <div class="summary-content">
              <div class="summary-hours">
                {{ memberAvailability.summary.total_hours }}h
              </div>
              <div class="summary-days">
                {{ memberAvailability.summary.total_days }} days
              </div>
            </div>
          </div>
        </div>

        <!-- Team Summary Row -->
        <div class="grid-row summary-row">
          <div class="member-column summary-cell">
            <strong>Team Total</strong>
          </div>
          <div
            v-for="day in sprintDays"
            :key="`summary-${day.date}`"
            class="day-column summary-cell"
          >
            <div class="day-summary">
              {{ getDaySummary(day.date || '') }}h
            </div>
          </div>
          <div class="summary-column summary-cell">
            <div class="team-summary">
              <div class="summary-hours">
                <strong>{{ availability.team_summary.total_hours }}h</strong>
              </div>
              <div class="summary-days">
                {{ availability.team_summary.total_days }} days
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref } from 'vue'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'
import { useSprintsStore, useMembersStore, useAppStore } from '@/stores'
import type { Sprint, DayAvailability, OverrideState } from '@/types'

interface Props {
  sprint?: Sprint | null
}

const props = defineProps<Props>()

const sprintsStore = useSprintsStore()
const membersStore = useMembersStore()
const appStore = useAppStore()

// Selection and bulk actions state
const selectionMode = ref(false)
const selectedCells = ref<Set<string>>(new Set())
const hoveredColumn = ref<string | null>(null)
const hoveredRow = ref<number | null>(null)


const loading = computed(() => sprintsStore.loading)
const availability = computed(() => sprintsStore.availability)
const members = computed(() => membersStore.members)

// Compute sprint days
const sprintDays = computed(() => {
  if (!props.sprint) return []

  const days = []
  const startDate = new Date(props.sprint.start_date)
  const endDate = new Date(props.sprint.end_date)

  for (let date = new Date(startDate); date <= endDate; date.setDate(date.getDate() + 1)) {
    const dayOfWeek = date.getDay()
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6

    days.push({
      date: date.toISOString().split('T')[0],
      dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
      displayDate: date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' }),
      isWeekend
    })
  }

  return days
})

// Helper functions
function getMemberRatio(memberId: number): number {
  const member = members.value.find(m => m.member_id === memberId)
  return member ? member.employment_ratio : 1
}

function formatEmploymentRatio(ratio: number): string {
  return `${Math.round(ratio * 100)}%`
}

function getMemberById(memberId: number) {
  return members.value.find(m => m.member_id === memberId)
}

function getWarningType(dayAvailability: DayAvailability): string | null {
  // Check for override on holiday or PTO
  if (dayAvailability.override_state &&
      (dayAvailability.auto_status === 'holiday' || dayAvailability.auto_status === 'pto')) {
    return `Override on ${dayAvailability.auto_status}`
  }

  return null
}

function getWarningIcon(dayAvailability: DayAvailability): string {
  const warningType = getWarningType(dayAvailability)
  if (warningType?.includes('holiday') || warningType?.includes('pto')) {
    return 'pi pi-exclamation-triangle'
  }
  return 'pi pi-info-circle'
}

function isOutsideAssignment(): boolean {
  // Assignment data not yet available from roster API
  // For now, we assume all days in sprint are within assignment
  return false
}

function getDayCellClass(dayAvailability: DayAvailability): string {
  const baseClass = 'availability-cell'
  const stateClass = `state-${dayAvailability.final_state}`
  const overrideClass = dayAvailability.override_state ? 'has-override' : ''
  const warningClass = getWarningType(dayAvailability) ? 'has-warning' : ''
  const outsideAssignmentClass = isOutsideAssignment() ? 'outside-assignment' : ''

  return `${baseClass} ${stateClass} ${overrideClass} ${warningClass} ${outsideAssignmentClass}`.trim()
}

function getDayCellTooltip(dayAvailability: DayAvailability, memberId: number): string {
  let tooltip = `Status: ${dayAvailability.final_state?.replace('_', ' ') || 'Unknown'}`

  if (dayAvailability.auto_status !== dayAvailability.final_state && dayAvailability.auto_status) {
    tooltip += `\nAuto: ${dayAvailability.auto_status.replace('_', ' ')}`
  }

  if (dayAvailability.override_state) {
    tooltip += `\nOverride: ${dayAvailability.override_state}`
  }

  if (dayAvailability.reason) {
    tooltip += `\nReason: ${dayAvailability.reason}`
  }

  // Add warning information
  const warningType = getWarningType(dayAvailability)
  if (warningType) {
    tooltip += `\n⚠️ Warning: ${warningType}`
  }

  if (isOutsideAssignment()) {
    tooltip += `\n🚫 Outside assignment period`
  }

  const member = getMemberById(memberId)
  if (member && !member.region_code) {
    tooltip += `\n⚪ No region set - holidays ignored`
  }

  return tooltip
}

function getDaySummary(date: string): number {
  if (!availability.value) return 0

  let totalHours = 0
  for (const member of availability.value.members) {
    const dayData = member.days.find(d => d.day === date)
    if (dayData) {
      const memberRatio = getMemberRatio(member.member_id)
      const dailyHours = 8 * memberRatio // Assuming 8-hour work day

      switch (dayData.final_state) {
        case 'available':
          totalHours += dailyHours
          break
        case 'half':
          totalHours += dailyHours / 2
          break
        // 'out', 'weekend', 'holiday', 'pto', 'out_of_assignment' contribute 0 hours
      }
    }
  }

  return Math.round(totalHours * 10) / 10 // Round to 1 decimal place
}

async function toggleAvailability(memberId: number, day: string, dayAvailability: DayAvailability) {
  if (!props.sprint) return

  // Can only override certain states
  if (['weekend', 'holiday'].includes(dayAvailability.auto_status)) {
    appStore.showWarning('Cannot override weekends or holidays')
    return
  }

  try {
    let newState: OverrideState = null

    // Cycle through override states
    if (!dayAvailability.override_state) {
      // No override -> set to 'out'
      newState = 'out'
    } else if (dayAvailability.override_state === 'out') {
      // Out -> half
      newState = 'half'
    } else if (dayAvailability.override_state === 'half') {
      // Half -> available
      newState = 'available'
    } else if (dayAvailability.override_state === 'available') {
      // Available -> remove override (clear override)
      // Set to null for no override
    } else {
      // Fallback case - should not happen
      return
    }

    await sprintsStore.updateAvailabilityOverride(
      props.sprint.sprint_id,
      memberId,
      day,
      newState,
      newState ? 'Manual override' : undefined
    )

  } catch (error) {
    console.error('Failed to update availability:', error)
    appStore.showError('Failed to update availability')
  }
}

async function refreshData() {
  if (!props.sprint) return

  try {
    await sprintsStore.fetchAvailability(props.sprint.sprint_id)
  } catch (error) {
    console.error('Failed to refresh availability:', error)
    appStore.showError('Failed to refresh availability data')
  }
}

// Bulk actions and selection functions
function enterSelectionMode() {
  selectionMode.value = true
  selectedCells.value.clear()
}

function exitSelectionMode() {
  selectionMode.value = false
  selectedCells.value.clear()
}

function clearSelection() {
  selectedCells.value.clear()
}

function getCellKey(memberId: number, day: string): string {
  return `${memberId}-${day}`
}

async function setBulkState(state: OverrideState) {
  if (!props.sprint || selectedCells.value.size === 0) return

  try {
    const updates = Array.from(selectedCells.value).map(cellKey => {
      const [memberIdStr, day] = cellKey.split('-')
      if (!memberIdStr || !day) {
        throw new Error('Invalid cell key format')
      }
      const memberId = Number.parseInt(memberIdStr, 10)
      return { memberId, day, state }
    })

    // Apply all updates
    for (const update of updates) {
      await sprintsStore.updateAvailabilityOverride(
        props.sprint.sprint_id,
        update.memberId,
        update.day,
        update.state,
        update.state ? 'Bulk update' : undefined
      )
    }

    appStore.showSuccess(`Updated ${updates.length} cells successfully`)
    clearSelection()
  } catch (error) {
    console.error('Failed to apply bulk update:', error)
    appStore.showError('Failed to apply bulk update')
  }
}

function selectColumn() {
  if (!hoveredColumn.value) return

  selectedCells.value.clear()

  // Add all cells in the hovered column
  if (availability.value) {
    for (const member of availability.value.members) {
      const cellKey = getCellKey(member.member_id, hoveredColumn.value)
      selectedCells.value.add(cellKey)
    }
  }
}

function isSelected(memberId: number, day: string): boolean {
  const cellKey = getCellKey(memberId, day)
  return selectedCells.value.has(cellKey)
}

function selectAll() {
  if (!availability.value?.members) return;

  for (const memberData of availability.value.members) {
    for (const dayAvailability of memberData.days) {
      const cellKey = getCellKey(memberData.member_id, dayAvailability.day)
      selectedCells.value.add(cellKey)
    }
  }
}

function selectWeekends() {
  if (!availability.value?.members) return;

  for (const memberData of availability.value.members) {
    for (const dayAvailability of memberData.days) {
      const date = new Date(dayAvailability.day)
      if (date.getDay() === 0 || date.getDay() === 6) { // Sunday or Saturday
        const cellKey = getCellKey(memberData.member_id, dayAvailability.day)
        selectedCells.value.add(cellKey)
      }
    }
  }
}

function handleCellClick(memberId: number, day: string, dayAvailability: DayAvailability) {
  if (selectionMode.value) {
    // Selection mode - toggle cell selection
    const cellKey = getCellKey(memberId, day)
    if (selectedCells.value.has(cellKey)) {
      selectedCells.value.delete(cellKey)
    } else {
      selectedCells.value.add(cellKey)
    }
  } else {
    // Normal mode - toggle availability
    toggleAvailability(memberId, day, dayAvailability)
  }
}

// Watch for sprint changes
watch(() => props.sprint, async (newSprint) => {
  if (newSprint) {
    await refreshData()
  }
}, { immediate: true })

// Load members data on mount
onMounted(async () => {
  try {
    await membersStore.fetchMembers()
  } catch (error) {
    console.error('Failed to load members:', error)
  }
})
</script>

<style scoped>
.availability-grid {
  width: 100%;
  max-width: 100vw;
  overflow-x: auto;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.grid-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.sprint-name {
  color: #7f8c8d;
  font-weight: normal;
  font-size: 1rem;
}

.grid-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 1rem;
}

.legend {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.status-cell {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid #dee2e6;
}

.status-cell.available {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.status-cell.out {
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.status-cell.half {
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.status-cell.weekend {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.status-cell.holiday {
  background-color: #d1ecf1;
  border-color: #bee5eb;
}

.status-cell.pto {
  background-color: #e2e3e5;
  border-color: #d6d8db;
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
}

.grid-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.grid-table {
  display: table;
  width: 100%;
  min-width: 800px;
}

.grid-row {
  display: table-row;
}

.header-row {
  background-color: #f8f9fa;
  font-weight: 600;
}

.member-row:nth-child(even) {
  background-color: #fdfdfe;
}

.member-row:hover {
  background-color: #f0f8ff;
}

.summary-row {
  background-color: #e9ecef;
  font-weight: 600;
  border-top: 2px solid #dee2e6;
}

.member-column {
  display: table-cell;
  width: 180px;
  min-width: 180px;
  padding: 0.75rem;
  vertical-align: middle;
  border-right: 1px solid #dee2e6;
}

.day-column {
  display: table-cell;
  width: 60px;
  min-width: 60px;
  padding: 0.5rem;
  vertical-align: middle;
  text-align: center;
  border-right: 1px solid #f1f3f4;
}

.summary-column {
  display: table-cell;
  width: 120px;
  min-width: 120px;
  padding: 0.75rem;
  vertical-align: middle;
  text-align: center;
}

.header-cell {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
}

.weekend-header {
  background-color: #f0f0f0;
}

.day-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.125rem;
}

.day-name {
  font-size: 0.75rem;
  font-weight: 600;
}

.day-date {
  font-size: 0.625rem;
  color: #6c757d;
}

.member-cell {
  border-bottom: 1px solid #f1f3f4;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.member-name {
  font-weight: 500;
  color: #2c3e50;
}

.member-ratio {
  font-size: 0.75rem;
  color: #6c757d;
}

.day-cell {
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.day-cell:hover {
  background-color: rgba(52, 152, 219, 0.1);
}

.availability-cell {
  height: 40px;
  position: relative;
}

.cell-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
}

.status-indicator {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.state-available .status-indicator {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.state-out .status-indicator {
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.state-half .status-indicator {
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.state-weekend .status-indicator {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.state-holiday .status-indicator {
  background-color: #d1ecf1;
  border-color: #bee5eb;
}

.state-pto .status-indicator {
  background-color: #e2e3e5;
  border-color: #d6d8db;
}

.state-out_of_assignment .status-indicator {
  background-color: #f0f0f0;
  border-color: #d0d0d0;
}

.has-override .status-indicator {
  box-shadow: 0 0 0 2px #007bff;
}

.has-warning {
  position: relative;
}

.has-warning .status-indicator {
  box-shadow: 0 0 0 1px #ffc107;
}

.outside-assignment {
  border: 2px solid #dc3545 !important;
}

.outside-assignment .status-indicator {
  opacity: 0.7;
}

.override-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.625rem;
  color: #007bff;
}

.warning-indicator {
  position: absolute;
  top: 2px;
  left: 2px;
  font-size: 0.625rem;
  color: #ffc107;
  z-index: 1;
}

.summary-cell {
  border-bottom: 1px solid #f1f3f4;
}

.summary-content,
.team-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.125rem;
}

.summary-hours {
  font-weight: 600;
  color: #2c3e50;
}

.summary-days {
  font-size: 0.75rem;
  color: #6c757d;
}

.day-summary {
  font-size: 0.875rem;
  font-weight: 500;
  color: #495057;
}

@media (max-width: 768px) {
  .grid-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .grid-controls {
    align-items: flex-start;
    width: 100%;
  }

  .legend {
    justify-content: flex-start;
  }

  .member-column {
    width: 140px;
    min-width: 140px;
  }

  .day-column {
    width: 50px;
    min-width: 50px;
  }

  .summary-column {
    width: 100px;
    min-width: 100px;
  }
}

/* Bulk Actions Toolbar Styles */
.bulk-actions-toolbar {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.selection-count {
  font-weight: 600;
  color: #495057;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.bulk-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-right: 0.5rem;
}

.selection-mode-controls {
  margin-left: auto;
}

.grid-controls-bar {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.keyboard-hint {
  color: #6c757d;
  font-size: 0.75rem;
}

.keyboard-hint kbd {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 3px;
  padding: 0.125rem 0.25rem;
  font-family: monospace;
  font-size: 0.7rem;
}

/* Selection indicator */
.selection-indicator {
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  color: #007bff;
  background: rgba(0, 123, 255, 0.1);
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

/* Selection mode styling */
.availability-grid[data-selection-mode="true"] .day-cell {
  cursor: pointer;
}

.availability-grid[data-selection-mode="true"] .day-cell:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

.day-cell.selected {
  background-color: rgba(0, 123, 255, 0.2) !important;
  border: 2px solid #007bff !important;
}

@media (max-width: 768px) {
  .bulk-actions-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .selection-mode-controls {
    margin-left: 0;
    margin-top: 0.5rem;
  }

  .grid-controls-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .keyboard-hint {
    text-align: center;
    margin-top: 0.5rem;
  }
}
</style>
