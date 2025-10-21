<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    :header="`Verfügbarkeit - ${sprint?.name || 'Sprint'}`"
    :style="{ width: '95vw', height: '85vh' }"
    :maximizable="true"
    :closable="true"
    class="availability-dialog"
  >
    <div class="availability-dialog-content">
      <div v-if="loading" class="loading-state">
        <ProgressSpinner size="50px" />
        <p>Lade Verfügbarkeitsdaten...</p>
      </div>

      <div v-else-if="!sprint" class="empty-state">
        <i class="pi pi-calendar-times empty-icon"></i>
        <h3>Kein Sprint ausgewählt</h3>
        <p>Bitte wählen Sie einen Sprint aus</p>
      </div>

      <div v-else-if="!availability?.members?.length" class="empty-state">
        <i class="pi pi-users empty-icon"></i>
        <h3>Keine Team-Mitglieder</h3>
        <p>Diesem Sprint sind noch keine Mitglieder zugeordnet. Fügen Sie zuerst Mitglieder über das Team Roster hinzu.</p>
        <Button 
          label="Team Roster öffnen" 
          icon="pi pi-users" 
          @click="$emit('open-roster')" 
          class="p-button-outlined mt-3"
        />
      </div>

      <div v-else class="grid-content">
        <!-- Controls & Info Bar -->
        <div class="grid-controls">
          <div class="control-group">
            <div class="filter-controls">
              <label class="checkbox-label">
                <Checkbox v-model="hideWeekends" binary />
                Wochenenden ausblenden
              </label>
            </div>
            <div class="summary-info">
              <div class="info-item">
                <i class="pi pi-users"></i>
                <span>{{ availability?.members?.length || 0 }} Mitglieder</span>
              </div>
              <div class="info-item">
                <i class="pi pi-clock"></i>
                <span>{{ availability?.team_summary?.total_hours || 0 }}h Gesamt</span>
              </div>
              <div class="info-item">
                <i class="pi pi-calendar"></i>
                <span>{{ filteredDays.length }} Tage</span>
              </div>
            </div>
          </div>
          <div class="grid-legend">
            <div class="legend-group">
              <span class="legend-title">Status:</span>
              <div class="legend-items">
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
                  <div class="status-dot weekend"></div>
                  <span>Wochenende</span>
                </div>
                <div class="legend-item">
                  <div class="status-dot holiday"></div>
                  <span>Feiertag</span>
                </div>
                <div class="legend-item">
                  <div class="status-dot pto"></div>
                  <span>Urlaub</span>
                </div>
              </div>
            </div>
            <div class="legend-hint">
              <i class="pi pi-info-circle"></i>
              <span>Klicken Sie auf eine Zelle um die Verfügbarkeit zu ändern</span>
            </div>
          </div>
        </div>

        <!-- Grid -->
        <div class="grid-table-container">
          <table class="availability-table">
            <!-- Header -->
            <thead>
              <tr>
                <th class="member-column">Team-Mitglied</th>
                <th
                  v-for="(day, index) in filteredDays"
                  :key="day.day"
                  class="day-column"
                  :class="{
                    'weekend-day': day.is_weekend,
                    'after-weekend': index > 0 && filteredDays[index - 1] && !filteredDays[index - 1]?.is_weekend && day.is_weekend
                  }"
                >
                  <div class="day-header">
                    <div class="day-name">{{ getDayName(day.day) }}</div>
                    <div class="day-date">{{ formatDayDate(day.day) }}</div>
                  </div>
                </th>
                <th class="summary-column">Summe</th>
              </tr>
            </thead>
            <!-- Body -->
            <tbody>
              <tr v-for="member in availability.members" :key="member.member_id" class="member-row">
                <td class="member-column">
                  <div class="member-info">
                    <div class="member-name">{{ member.member_name }}</div>
                    <div class="member-details">
                      <span class="allocation">{{ Math.round(member.allocation * 100) }}%</span>
                    </div>
                  </div>
                </td>
                <td
                  v-for="(day, dayIndex) in member.days.filter(d => !hideWeekends || !isWeekendDay(d.day))"
                  :key="day.day"
                  class="availability-cell"
                  :class="[
                    getAvailabilityClass(day),
                    {
                      'weekend-day': isWeekendDay(day.day),
                      'after-weekend': dayIndex > 0 && !isWeekendDay(member.days.filter(d => !hideWeekends || !isWeekendDay(d.day))[dayIndex - 1]?.day || '') && isWeekendDay(day.day)
                    }
                  ]"
                  :title="getAvailabilityTooltip(day, member.member_name)"
                  @click="toggleAvailability(member.member_id, day.day, day)"
                >
                  <div class="status-dot" :class="getAvailabilityClass(day)"></div>
                </td>
                <td class="summary-column">
                  <div class="member-summary">
                    <div class="hours">{{ member.summary?.total_hours || 0 }}h</div>
                    <div class="days">{{ member.summary?.total_days || 0 }} Tage</div>
                  </div>
                </td>
              </tr>
              <!-- Team Totals -->
              <tr class="team-totals-row">
                <td class="member-column">
                  <strong>Team Gesamt</strong>
                </td>
                <td
                  v-for="day in filteredDays"
                  :key="`total-${day.day}`"
                  class="availability-cell total-cell"
                  :class="{ 'weekend-day': day.is_weekend }"
                >
                  <div class="day-total">{{ getDayTotal(day.day) }}</div>
                </td>
                <td class="summary-column">
                  <div class="team-summary">
                    <div class="hours">{{ availability.team_summary?.total_hours || 0 }}h</div>
                    <div class="days">{{ availability.team_summary?.total_days || 0 }} Tage</div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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

// Store & Utils


// Reactive state
const hideWeekends = ref(false)

// Computed properties
const filteredDays = computed(() => {
  if (!props.availability?.members?.length) return []

  const allDays = props.availability.members[0]?.days?.map(d => ({
    day: d.day,
    is_weekend: isWeekendDay(d.day)
  })) || []

  if (hideWeekends.value) {
    return allDays.filter(day => !day.is_weekend)
  }
  return allDays
})

// Functions
const isWeekendDay = (dateString: string) => {
  const date = new Date(dateString)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 0 || dayOfWeek === 6 // Sunday or Saturday
}

const getDayName = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('de-DE', { weekday: 'short' })
}

const formatDayDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit'
  })
}

const getAvailabilityClass = (day: DayAvailability) => {
  const finalState = day.final_state as string

  switch (finalState) {
    case 'available':
      return 'available'
    case 'half':
      return 'half-available'
    case 'out':
    case 'pto':
      return 'unavailable'
    case 'holiday':
      return 'holiday'
    case 'weekend':
      return 'weekend'
    case 'out_of_assignment':
      return 'outside'
    default:
      return 'unknown'
  }
}

const getAvailabilityTooltip = (day: DayAvailability, memberName: string) => {
  const date = day.day as string
  const finalState = day.final_state as string
  const reason = day.reason as string || ''

  const stateText = {
    available: 'Verfügbar',
    half: 'Teilweise verfügbar',
    out: 'Nicht verfügbar',
    pto: 'Urlaub',
    holiday: 'Feiertag',
    weekend: 'Wochenende',
    out_of_assignment: 'Außerhalb Zuordnung'
  }[finalState] || 'Unbekannt'

  return `${memberName} - ${new Date(date).toLocaleDateString('de-DE')}: ${stateText}${reason ? ` (${reason})` : ''}`
}

const getDayTotal = (date: string) => {
  if (!props.availability?.members) return 0

  let total = 0
  props.availability.members.forEach(member => {
    const day = member.days.find(d => d.day === date)
    if (day) {
      switch (day.final_state) {
        case 'available':
          total += 1
          break
        case 'half':
          total += 0.5
          break
      }
    }
  })
  return total
}

const toggleAvailability = async (memberId: number, date: string, currentDay: DayAvailability) => {
  emit('toggle-availability', memberId, date, currentDay)
}

// Watch for sprint changes to reset weekend filter
watch(() => props.sprint, () => {
  hideWeekends.value = false
})
</script>

<style scoped>
.availability-dialog-content {
  height: calc(90vh - 120px);
  display: flex;
  flex-direction: column;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-color-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: var(--surface-400);
}

.grid-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.grid-controls {
  padding: 1.5rem;
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-border);
  border-radius: 6px 6px 0 0;
}

.control-group {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 1rem;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.summary-info {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid var(--surface-border);
}

.info-item i {
  color: var(--primary-color);
}

.grid-legend {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.legend-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.legend-title {
  font-weight: 600;
  color: var(--text-color);
  margin-right: 0.5rem;
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
  color: var(--text-color-secondary);
}

.legend-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  background: var(--blue-50);
  color: var(--blue-700);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border-left: 3px solid var(--blue-500);
}

.grid-table-container {
  flex: 1;
  overflow: auto;
  border: 1px solid var(--surface-border);
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
  border: 1px solid var(--surface-border);
  text-align: center;
  vertical-align: middle;
}

.member-column {
  min-width: 180px;
  background: var(--surface-50);
  font-weight: 600;
  position: sticky;
  left: 0;
  z-index: 10;
  text-align: left;
  padding: 0.5rem;
}

.day-column {
  min-width: 60px;
  background: var(--surface-100);
  padding: 0.5rem 0.25rem;
}

.day-column.weekend-day {
  background: var(--orange-100);
  color: var(--orange-800);
}

.day-column.after-weekend {
  border-left: 3px solid var(--primary-color);
}

.summary-column {
  min-width: 100px;
  background: var(--surface-50);
  font-weight: 600;
  position: sticky;
  right: 0;
  z-index: 10;
}

.day-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.day-name {
  font-weight: 600;
  font-size: 0.75rem;
}

.day-date {
  font-size: 0.7rem;
  opacity: 0.8;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.member-name {
  font-weight: 600;
}

.member-details {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.allocation {
  background: var(--primary-100);
  color: var(--primary-800);
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  display: inline-block;
}

.availability-cell {
  padding: 0.75rem 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.availability-cell:hover {
  background: var(--primary-50) !important;
  transform: scale(1.05);
}

.availability-cell:hover .status-dot {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.availability-cell.weekend-day {
  background: var(--orange-50);
}

.availability-cell.after-weekend {
  border-left: 3px solid var(--primary-color);
}

.status-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin: 0 auto;
  border: 2px solid rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-dot.available {
  background: linear-gradient(135deg, var(--green-400), var(--green-600));
  border-color: var(--green-200);
}

.status-dot.available::after {
  content: '✓';
  color: white;
  font-weight: bold;
  font-size: 12px;
}

.status-dot.half-available {
  background: linear-gradient(90deg, var(--orange-500) 50%, var(--orange-200) 50%);
  border-color: var(--orange-300);
}

.status-dot.half-available::after {
  content: '½';
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.status-dot.unavailable {
  background: linear-gradient(135deg, var(--red-400), var(--red-600));
  border-color: var(--red-200);
}

.status-dot.unavailable::after {
  content: '✗';
  color: white;
  font-weight: bold;
  font-size: 12px;
}

.status-dot.weekend {
  background: linear-gradient(135deg, var(--surface-400), var(--surface-500));
  border-color: var(--surface-300);
}

.status-dot.holiday {
  background: linear-gradient(135deg, var(--purple-400), var(--purple-600));
  border-color: var(--purple-200);
}

.status-dot.holiday::after {
  content: '🎉';
  font-size: 10px;
}

.status-dot.pto {
  background: linear-gradient(135deg, var(--blue-400), var(--blue-600));
  border-color: var(--blue-200);
}

.status-dot.pto::after {
  content: '🏖️';
  font-size: 10px;
}

.status-dot.outside {
  background: var(--surface-200);
  border: 2px dashed var(--surface-500);
}

.status-dot.unknown {
  background: var(--surface-200);
  border-color: var(--surface-400);
}

.status-dot.unknown::after {
  content: '?';
  color: var(--surface-600);
  font-weight: bold;
  font-size: 12px;
}

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
}

.days {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.team-totals-row {
  background: var(--surface-100) !important;
  font-weight: 600;
}

.team-totals-row td {
  background: var(--surface-100) !important;
  border-top: 2px solid var(--surface-300);
}

.day-total {
  font-weight: 600;
  color: var(--primary-color);
}

.total-cell {
  cursor: default;
}

.total-cell:hover {
  background: var(--surface-100) !important;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .grid-controls {
    padding: 1rem;
  }

  .control-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .summary-info {
    gap: 1rem;
  }

  .info-item {
    font-size: 0.75rem;
    padding: 0.25rem 0.75rem;
  }

  .legend-items {
    gap: 1rem;
  }

  .legend-item {
    font-size: 0.75rem;
  }

  .member-column {
    min-width: 120px;
    font-size: 0.8rem;
  }

  .day-column {
    min-width: 45px;
  }

  .status-dot {
    width: 20px;
    height: 20px;
  }

  .status-dot::after {
    font-size: 10px;
  }
}

@media (max-width: 768px) {
  .availability-dialog-content {
    height: calc(100vh - 120px);
  }

  .grid-controls {
    padding: 0.75rem;
  }

  .legend-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .legend-hint {
    font-size: 0.7rem;
    padding: 0.375rem 0.75rem;
  }

  .member-column {
    min-width: 100px;
    font-size: 0.75rem;
  }

  .day-column {
    min-width: 40px;
    padding: 0.25rem 0.125rem;
  }

  .day-name {
    font-size: 0.7rem;
  }

  .day-date {
    font-size: 0.65rem;
  }

  .availability-cell {
    padding: 0.5rem 0.25rem;
  }

  .status-dot {
    width: 18px;
    height: 18px;
  }

  .status-dot::after {
    font-size: 8px;
  }

  .summary-column {
    min-width: 80px;
    font-size: 0.75rem;
  }

  .hours,
  .days {
    font-size: 0.7rem;
  }
}
</style>
