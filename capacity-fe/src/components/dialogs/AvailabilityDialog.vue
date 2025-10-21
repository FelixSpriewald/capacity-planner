<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    :header="`Verfügbarkeit - ${sprint?.name || 'Sprint'}`"
    :style="{ width: '90vw', height: '80vh' }"
    :maximizable="true"
    :closable="true"
    class="availability-dialog"
  >
    <div class="availability-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <ProgressSpinner size="50px" />
        <p>Lade Verfügbarkeitsdaten...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="!availability?.members?.length" class="empty-container">
        <i class="pi pi-users empty-icon"></i>
        <h3>Keine Team-Mitglieder</h3>
        <p>Diesem Sprint sind noch keine Mitglieder zugeordnet.</p>
        <Button 
          label="Team Roster öffnen" 
          icon="pi pi-users" 
          @click="$emit('open-roster')" 
          class="p-button-outlined"
        />
      </div>

      <!-- Main Content -->
      <div v-else class="availability-main">
        <!-- Controls -->
        <div class="controls-bar">
          <div class="filters">
            <div class="filter-item">
              <Checkbox v-model="hideWeekends" binary />
              <label>Wochenenden ausblenden</label>
            </div>
          </div>
          
          <div class="summary">
            <div class="summary-item">
              <i class="pi pi-users"></i>
              <span>{{ availability.members.length }} Mitglieder</span>
            </div>
            <div class="summary-item">
              <i class="pi pi-clock"></i>
              <span>{{ availability.team_summary?.total_hours || 0 }}h</span>
            </div>
            <div class="summary-item">
              <i class="pi pi-calendar"></i>
              <span>{{ visibleDays.length }} Tage</span>
            </div>
          </div>
        </div>

        <!-- Legend -->
        <div class="legend-bar">
          <div class="legend-title">Status-Legende:</div>
          <div class="legend-items">
            <div class="legend-item">
              <div class="status-indicator available"></div>
              <span>Verfügbar</span>
            </div>
            <div class="legend-item">
              <div class="status-indicator half"></div>
              <span>Halbtags</span>
            </div>
            <div class="legend-item">
              <div class="status-indicator unavailable"></div>
              <span>Nicht verfügbar</span>
            </div>
            <div class="legend-item">
              <div class="status-indicator weekend"></div>
              <span>Wochenende</span>
            </div>
            <div class="legend-item">
              <div class="status-indicator holiday"></div>
              <span>Feiertag</span>
            </div>
          </div>
          <div class="legend-hint">
            <i class="pi pi-info-circle"></i>
            <span>Klicken Sie auf eine Zelle um die Verfügbarkeit zu ändern</span>
          </div>
        </div>

        <!-- Availability Grid -->
        <div class="grid-container">
          <div class="grid-wrapper">
            <table class="availability-grid">
              <!-- Header -->
              <thead>
                <tr>
                  <th class="member-header">Team-Mitglied</th>
                  <th 
                    v-for="day in visibleDays" 
                    :key="day.date"
                    class="day-header"
                    :class="{ 'weekend': day.isWeekend }"
                  >
                    <div class="day-info">
                      <div class="day-name">{{ day.dayName }}</div>
                      <div class="day-date">{{ day.displayDate }}</div>
                    </div>
                  </th>
                  <th class="summary-header">Summe</th>
                </tr>
              </thead>

              <!-- Body -->
              <tbody>
                <tr v-for="member in availability.members" :key="member.member_id" class="member-row">
                  <td class="member-cell">
                    <div class="member-info">
                      <div class="member-name">{{ member.member_name }}</div>
                      <div class="member-allocation">{{ Math.round(member.allocation * 100) }}%</div>
                    </div>
                  </td>
                  
                  <td 
                    v-for="day in getVisibleDaysForMember(member)" 
                    :key="day.day"
                    class="availability-cell"
                    :class="getStatusClass(day)"
                    @click="handleCellClick(member.member_id, day.day, day)"
                  >
                    <div class="cell-content">
                      <div 
                        class="status-dot" 
                        :class="getStatusClass(day)"
                        :title="getTooltip(member.member_name, day)"
                      ></div>
                    </div>
                  </td>

                  <td class="summary-cell">
                    <div class="member-summary">
                      <div class="hours">{{ member.summary?.total_hours || 0 }}h</div>
                      <div class="days">{{ member.summary?.total_days || 0 }}d</div>
                    </div>
                  </td>
                </tr>

                <!-- Team Totals -->
                <tr class="totals-row">
                  <td class="member-cell totals-label">
                    <strong>Team Gesamt</strong>
                  </td>
                  <td 
                    v-for="day in visibleDays" 
                    :key="`total-${day.date}`"
                    class="total-cell"
                  >
                    <div class="day-total">{{ getDayTotal(day.date) }}</div>
                  </td>
                  <td class="summary-cell">
                    <div class="team-summary">
                      <div class="hours">{{ availability.team_summary?.total_hours || 0 }}h</div>
                      <div class="days">{{ availability.team_summary?.total_days || 0 }}d</div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'

import type { Sprint, DayAvailability, AvailabilityResponse } from '@/types/index'

// Props & Emits
interface Props {
  visible: boolean
  sprint: Sprint | null
  loading?: boolean
  availability?: AvailabilityResponse | null
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  availability: null
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'toggle-availability': [memberId: number, date: string, currentDay: DayAvailability]
  'open-roster': []
}>()

// State
const hideWeekends = ref(false)

// Computed
const visibleDays = computed(() => {
  if (!props.availability?.members?.length) return []
  
  const firstMember = props.availability.members[0]
  if (!firstMember?.days?.length) return []

  return firstMember.days
    .filter(day => !hideWeekends.value || !isWeekend(day.day))
    .map(day => ({
      date: day.day,
      dayName: getDayName(day.day),
      displayDate: getDisplayDate(day.day),
      isWeekend: isWeekend(day.day)
    }))
})

// Functions
const isWeekend = (dateString: string) => {
  const date = new Date(dateString)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 0 || dayOfWeek === 6
}

const getDayName = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('de-DE', { weekday: 'short' })
}

const getDisplayDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit'
  })
}

const getVisibleDaysForMember = (member: { days: DayAvailability[] }) => {
  return member.days.filter((day: DayAvailability) => 
    !hideWeekends.value || !isWeekend(day.day)
  )
}

const getStatusClass = (day: DayAvailability) => {
  const state = day.final_state
  
  switch (state) {
    case 'available':
      return 'available'
    case 'half':
      return 'half'
    case 'out':
    case 'pto':
      return 'unavailable'
    case 'holiday':
      return 'holiday'
    case 'weekend':
      return 'weekend'
    default:
      return 'unknown'
  }
}

const getTooltip = (memberName: string, day: DayAvailability) => {
  const date = new Date(day.day).toLocaleDateString('de-DE')
  const stateLabels: Record<string, string> = {
    available: 'Verfügbar',
    half: 'Halbtags',
    out: 'Nicht verfügbar',
    pto: 'Urlaub',
    holiday: 'Feiertag',
    weekend: 'Wochenende'
  }
  
  const stateLabel = stateLabels[day.final_state] || 'Unbekannt'
  return `${memberName} - ${date}: ${stateLabel}`
}

const getDayTotal = (date: string) => {
  if (!props.availability?.members) return 0
  
  return props.availability.members.reduce((total, member) => {
    const day = member.days.find(d => d.day === date)
    if (!day) return total
    
    switch (day.final_state) {
      case 'available':
        return total + 1
      case 'half':
        return total + 0.5
      default:
        return total
    }
  }, 0)
}

const handleCellClick = (memberId: number, date: string, day: DayAvailability) => {
  // Don't allow editing weekends or holidays
  if (day.final_state === 'weekend' || day.final_state === 'holiday') {
    return
  }
  
  emit('toggle-availability', memberId, date, day)
}
</script>

<style scoped>
.availability-dialog {
  .p-dialog-content {
    padding: 0;
    height: 100%;
  }
}

.availability-content {
  height: calc(80vh - 120px);
  display: flex;
  flex-direction: column;
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: var(--surface-400);
  margin-bottom: 1rem;
}

.availability-main {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-border);
}

.filters {
  display: flex;
  gap: 1rem;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-item label {
  cursor: pointer;
  font-weight: 500;
}

.summary {
  display: flex;
  gap: 2rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid var(--surface-border);
  font-size: 0.875rem;
}

.summary-item i {
  color: var(--primary-color);
}

.legend-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 1.5rem;
  background: var(--surface-100);
  border-bottom: 1px solid var(--surface-border);
  flex-wrap: wrap;
}

.legend-title {
  font-weight: 600;
  color: var(--text-color);
}

.legend-items {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.legend-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  background: var(--blue-50);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border-left: 3px solid var(--blue-500);
  margin-left: auto;
}

.status-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.status-indicator.available { background: var(--green-500); }
.status-indicator.half { background: var(--orange-500); }
.status-indicator.unavailable { background: var(--red-500); }
.status-indicator.weekend { background: var(--surface-400); }
.status-indicator.holiday { background: var(--purple-500); }

.grid-container {
  flex: 1;
  overflow: auto;
  padding: 1rem;
}

.grid-wrapper {
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  overflow: hidden;
}

.availability-grid {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.availability-grid th,
.availability-grid td {
  padding: 0;
  border: 1px solid var(--surface-border);
  text-align: center;
  vertical-align: middle;
}

.member-header,
.member-cell {
  min-width: 180px;
  text-align: left;
  padding: 1rem;
  background: var(--surface-50);
  position: sticky;
  left: 0;
  z-index: 10;
}

.day-header {
  min-width: 60px;
  padding: 0.75rem 0.5rem;
  background: var(--surface-100);
}

.day-header.weekend {
  background: var(--orange-100);
  color: var(--orange-800);
}

.summary-header,
.summary-cell {
  min-width: 100px;
  padding: 1rem;
  background: var(--surface-50);
  position: sticky;
  right: 0;
  z-index: 10;
}

.day-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.day-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.day-date {
  font-size: 0.75rem;
  opacity: 0.8;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.member-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.member-allocation {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  background: var(--primary-100);
  color: var(--primary-800);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  display: inline-block;
  width: fit-content;
}

.availability-cell {
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.availability-cell:hover {
  background: var(--primary-50);
}

.availability-cell.weekend,
.availability-cell.holiday {
  cursor: not-allowed;
  opacity: 0.7;
}

.cell-content {
  display: flex;
  justify-content: center;
  align-items: center;
}

.status-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: all 0.2s ease;
}

.availability-cell:hover .status-dot {
  transform: scale(1.1);
}

.status-dot.available { background: var(--green-500); }
.status-dot.half { background: var(--orange-500); }
.status-dot.unavailable { background: var(--red-500); }
.status-dot.weekend { background: var(--surface-400); }
.status-dot.holiday { background: var(--purple-500); }
.status-dot.unknown { background: var(--surface-300); }

.member-summary,
.team-summary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: center;
}

.hours {
  font-weight: 600;
  color: var(--green-600);
  font-size: 0.875rem;
}

.days {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.totals-row {
  background: var(--surface-100);
  font-weight: 600;
}

.totals-row td {
  border-top: 2px solid var(--surface-300);
}

.totals-label {
  background: var(--surface-100) !important;
}

.total-cell {
  background: var(--surface-100);
  padding: 0.75rem;
}

.day-total {
  font-weight: 600;
  color: var(--primary-color);
}

/* Responsive */
@media (max-width: 1024px) {
  .controls-bar {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .legend-bar {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .legend-hint {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .member-header,
  .member-cell {
    min-width: 140px;
    padding: 0.75rem;
  }
  
  .day-header {
    min-width: 50px;
    padding: 0.5rem 0.25rem;
  }
  
  .summary-header,
  .summary-cell {
    min-width: 80px;
    padding: 0.75rem;
  }
  
  .availability-cell {
    padding: 0.5rem;
  }
  
  .status-dot {
    width: 16px;
    height: 16px;
  }
}
</style>