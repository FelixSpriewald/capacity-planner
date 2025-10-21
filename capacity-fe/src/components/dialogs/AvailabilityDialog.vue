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
.availability-dialog :deep(.p-dialog-content) {
  padding: 0;
  height: 100%;
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
  padding: 3rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.loading-container p,
.empty-container h3,
.empty-container p {
  color: #6b7280;
  margin: 0.5rem 0;
}

.empty-container h3 {
  color: #374151;
  font-size: 1.25rem;
  font-weight: 600;
}

.empty-icon {
  font-size: 4rem;
  color: #9ca3af;
  margin-bottom: 1.5rem;
  opacity: 0.8;
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
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filters {
  display: flex;
  gap: 1.5rem;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.filter-item label {
  cursor: pointer;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.filter-item:hover {
  background: #f9fafb;
  border-color: #3b82f6;
}

.summary {
  display: flex;
  gap: 1.5rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.summary-item:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.summary-item i {
  color: #3b82f6;
  font-size: 1rem;
}

.legend-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  flex-wrap: wrap;
  min-height: 60px;
}

.legend-title {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
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
  font-size: 0.8125rem;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  background: white;
  border: 1px solid #f3f4f6;
}

.legend-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #1e40af;
  background: #dbeafe;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
  margin-left: auto;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.status-indicator {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
  flex-shrink: 0;
}

.status-indicator.available { 
  background: linear-gradient(135deg, #10b981, #059669);
}
.status-indicator.half { 
  background: linear-gradient(90deg, #f59e0b 50%, #fbbf24 50%);
}
.status-indicator.unavailable { 
  background: linear-gradient(135deg, #ef4444, #dc2626);
}
.status-indicator.weekend { 
  background: linear-gradient(135deg, #9ca3af, #6b7280);
}
.status-indicator.holiday { 
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.grid-container {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
  background: #f9fafb;
}

.grid-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  background: white;
}

.availability-grid {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 0.875rem;
}

.availability-grid th,
.availability-grid td {
  padding: 0;
  border: 1px solid #f3f4f6;
  text-align: center;
  vertical-align: middle;
  transition: all 0.2s ease;
}

.member-header,
.member-cell {
  min-width: 200px;
  text-align: left;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  position: sticky;
  left: 0;
  z-index: 10;
  border-right: 2px solid #e2e8f0;
  font-weight: 500;
}

.day-header {
  min-width: 70px;
  padding: 1rem 0.75rem;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  font-weight: 600;
  color: #374151;
}

.day-header.weekend {
  background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
  color: #92400e;
}

.summary-header,
.summary-cell {
  min-width: 120px;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  position: sticky;
  right: 0;
  z-index: 10;
  border-left: 2px solid #e2e8f0;
  font-weight: 500;
}

.day-info {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  align-items: center;
}

.day-name {
  font-weight: 700;
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1;
}

.day-date {
  font-size: 0.75rem;
  font-weight: 500;
  opacity: 0.9;
  line-height: 1;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.member-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: #1f2937;
  line-height: 1.2;
}

.member-allocation {
  font-size: 0.8125rem;
  font-weight: 600;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  display: inline-block;
  width: fit-content;
  border: 1px solid #93c5fd;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.availability-cell {
  padding: 1rem 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.availability-cell:hover {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  transform: scale(1.02);
}

.availability-cell.weekend,
.availability-cell.holiday {
  cursor: not-allowed;
  opacity: 0.6;
  background: #f9fafb;
}

.availability-cell.weekend:hover,
.availability-cell.holiday:hover {
  transform: none;
  background: #f9fafb;
}

.cell-content {
  display: flex;
  justify-content: center;
  align-items: center;
}

.status-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
  transition: all 0.3s ease;
  position: relative;
}

.availability-cell:hover .status-dot {
  transform: scale(1.15);
  box-shadow: 0 6px 12px rgba(0,0,0,0.2), 0 6px 12px rgba(0,0,0,0.25);
}

.status-dot.available { 
  background: linear-gradient(135deg, #10b981, #059669);
}

.status-dot.half { 
  background: linear-gradient(90deg, #f59e0b 50%, #fbbf24 50%);
}

.status-dot.unavailable { 
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.status-dot.weekend { 
  background: linear-gradient(135deg, #9ca3af, #6b7280);
}

.status-dot.holiday { 
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.status-dot.unknown { 
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
}

.member-summary,
.team-summary {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  align-items: center;
}

.hours {
  font-weight: 700;
  color: #059669;
  font-size: 1rem;
  line-height: 1;
}

.days {
  font-size: 0.8125rem;
  color: #6b7280;
  font-weight: 500;
}

.totals-row {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  font-weight: 700;
}

.totals-row td {
  border-top: 3px solid #3b82f6;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
}

.totals-label {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%) !important;
  color: #1f2937;
}

.total-cell {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  padding: 1rem 0.75rem;
}

.day-total {
  font-weight: 700;
  color: #1e40af;
  font-size: 1rem;
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