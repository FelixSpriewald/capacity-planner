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
            <!-- Wochenenden werden automatisch ausgeblendet -->
          </div>

          <div class="legend-inline">
            <div class="legend-items-compact">
              <div class="legend-item-compact">
                <div class="status-indicator available"></div>
                <span>Verfügbar</span>
              </div>
              <div class="legend-item-compact">
                <div class="status-indicator half"></div>
                <span>Halbtags</span>
              </div>
              <div class="legend-item-compact">
                <div class="status-indicator unavailable"></div>
                <span>Nicht verfügbar</span>
              </div>
              <div class="legend-item-compact">
                <div class="status-indicator holiday"></div>
                <span>Feiertag</span>
              </div>
            </div>
          </div>

          <div class="summary">
            <div class="summary-item">
              <i class="pi pi-users"></i>
              <span>{{ availability.members.length }} Mitglieder</span>
            </div>
            <div class="summary-item">
              <i class="pi pi-calendar"></i>
              <span>{{ visibleDays.length }} Tage</span>
            </div>
            <div class="summary-item">
              <i class="pi pi-calendar"></i>
              <span>{{ availability.sum_days_team || availability.team_summary?.total_days || 0 }} Gesamt-Tage</span>
            </div>
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
                    :class="{
                      'weekend': day.isWeekend,
                      'weekend-separator': day.showWeekendSeparator
                    }"
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
                      <div class="member-name">{{ member.member_name || member.name || `Member ${member.member_id}` }}</div>
                      <div class="member-allocation">{{ Math.round((member.allocation || 1) * 100) }}%</div>
                    </div>
                  </td>

                  <td
                    v-for="day in visibleDays"
                    :key="`${member.member_id}-${day.date}`"
                    class="availability-cell"
                    :class="{
                      'weekend': day.isWeekend,
                      'weekend-separator': day.showWeekendSeparator,
                      'clickable': getMemberDay(member, day.date)?.final_state !== 'weekend' && getMemberDay(member, day.date)?.final_state !== 'holiday'
                    }"
                    @click="getMemberDay(member, day.date) && handleCellClick(member.member_id, day.date, getMemberDay(member, day.date))"
                    :title="getMemberDay(member, day.date) ? getTooltip(member.member_name || member.name || `Member ${member.member_id}`, getMemberDay(member, day.date)) : ''"
                  >
                    <div
                      v-if="getMemberDay(member, day.date)"
                      class="status-indicator"
                      :class="getStatusClass(getMemberDay(member, day.date))"
                    ></div>
                  </td>

                  <td class="summary-cell">
                    <div class="member-summary">
                      <div class="days">{{ member.sum_days || member.summary?.total_days || 0 }}d</div>
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
                    :class="{ 'weekend-separator': day.showWeekendSeparator }"
                  >
                    <div class="day-total">{{ getDayTotal(day.date) }}</div>
                  </td>
                  <td class="summary-cell">
                    <div class="team-summary">
                      <div class="days">{{ availability.sum_days_team || availability.team_summary?.total_days || 0 }}d</div>
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
import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
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
// Wochenenden werden automatisch ausgeblendet

// Computed
const visibleDays = computed(() => {
  if (!props.availability?.members?.length) return []

  const firstMember = props.availability.members[0]
  if (!firstMember?.days?.length) return []

  const result = firstMember.days
    .filter(day => {
      // Handle actual data structure - check multiple possible date fields
      const dateField = (day as any).day || (day as any).date || (day as any).dateString || (day as any).day_date
      return dateField && !isWeekend(dateField)
    })
    .map((day, index, filteredDays) => {
      const dateField = (day as any).day || (day as any).date || (day as any).dateString || (day as any).day_date
      const previousDay = index > 0 ? filteredDays[index - 1] : null
      const previousDateField = previousDay ? ((previousDay as any).day || (previousDay as any).date || (previousDay as any).dateString || (previousDay as any).day_date) : null
      const showWeekendSeparator = previousDay && hasWeekendBetween(previousDateField, dateField)

      return {
        date: dateField,
        dayName: getDayName(dateField),
        displayDate: getDisplayDate(dateField),
        isWeekend: isWeekend(dateField),
        showWeekendSeparator
      }
    })

  return result
})

// Functions
const isWeekend = (dateString: string) => {
  const date = new Date(dateString)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 0 || dayOfWeek === 6
}

const getDayName = (dateString: string) => {
  if (!dateString) return 'N/A'
  // Backend liefert Format YYYY-MM-DD
  const date = new Date(dateString + 'T00:00:00')
  if (isNaN(date.getTime())) {
    console.log('Invalid date:', dateString)
    return dateString
  }
  return date.toLocaleDateString('de-DE', { weekday: 'short' })
}

const getDisplayDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  // Backend liefert Format YYYY-MM-DD
  const date = new Date(dateString + 'T00:00:00')
  if (isNaN(date.getTime())) {
    // Fallback: YYYY-MM-DD direkt formatieren
    const parts = dateString.split('-')
    if (parts.length === 3) {
      return `${parts[2]}.${parts[1]}`
    }
    return dateString
  }
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit'
  })
}





const hasWeekendBetween = (date1: string, date2: string) => {
  const d1 = new Date(date1)
  const d2 = new Date(date2)
  const diffDays = Math.floor((d2.getTime() - d1.getTime()) / (1000 * 60 * 60 * 24))
  return diffDays > 1 // Mehr als 1 Tag Unterschied bedeutet Wochenende dazwischen
}

const getMemberDay = (member: { days?: DayAvailability[] }, date: string) => {
  return member.days?.find(d => {
    const dayDate = (d as any).day || (d as any).date || (d as any).dateString || (d as any).day_date
    return dayDate === date
  }) || null
}

const getStatusClass = (day: DayAvailability | null) => {
  if (!day) return 'unknown'

  const state = day.final_state
  const overrideState = day.override_state

  // Status detection logic

  // Priority: override_state takes precedence if it exists
  if (overrideState !== null && overrideState !== undefined) {
    switch (overrideState) {
      case 'available':
        return 'available'
      case 'half':
        return 'half'
      case 'out':
        return 'unavailable'
      default:
        return 'unavailable' // Any other override should be unavailable
    }
  }

  // Fall back to final_state
  switch (state) {
    case 'available':
      return 'available'
    case 'half':
      return 'half'
    case 'out':
    case 'pto':
    case 'out_of_assignment':
      return 'unavailable'
    case 'holiday':
      return 'holiday'
    case 'weekend':
      return 'weekend'
    default:
      console.log('Unknown state detected:', state)
      return 'unknown'
  }
}

const getTooltip = (memberName: string, day: DayAvailability | null) => {
  if (!day) return ''

  // Handle the actual data structure for date
  const dayDate = (day as any).day || (day as any).date || (day as any).dateString || (day as any).day_date
  let formattedDate = 'Unbekanntes Datum'

  if (dayDate) {
    const date = new Date(dayDate + 'T00:00:00')
    if (!isNaN(date.getTime())) {
      formattedDate = date.toLocaleDateString('de-DE')
    } else {
      // Fallback for YYYY-MM-DD format
      const parts = dayDate.split('-')
      if (parts.length === 3) {
        formattedDate = `${parts[2]}.${parts[1]}.${parts[0]}`
      }
    }
  }

  const stateLabels: Record<string, string> = {
    available: 'Verfügbar',
    half: 'Halbtags',
    out: 'Nicht verfügbar',
    unavailable: 'Nicht verfügbar',
    pto: 'Urlaub',
    holiday: 'Feiertag',
    weekend: 'Wochenende'
  }

  const stateLabel = stateLabels[day.final_state] || `Unbekannt (${day.final_state})`
  const memberDisplayName = memberName || 'Unbekanntes Mitglied'
  return `${memberDisplayName} - ${formattedDate}: ${stateLabel}`
}

const getDayTotal = (date: string) => {
  if (!props.availability?.members) return '0'

  let total = 0
  props.availability.members.forEach(member => {
    // Handle the actual data structure - check multiple possible date fields
    const day = member.days?.find(d => {
      const dayDate = (d as any).day || (d as any).date || (d as any).dateString || (d as any).day_date
      return dayDate === date
    })
    if (day && day.final_state === 'available') {
      const allocation = Number(member.allocation) || 1
      total += allocation
    } else if (day && day.final_state === 'half') {
      const allocation = Number(member.allocation) || 1
      total += allocation * 0.5
    }
  })

  return String(Number(total).toFixed(1))
}

const handleCellClick = (memberId: number, date: string, day: DayAvailability | null) => {
  if (!day) return
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
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.availability-dialog :deep(.p-dialog-header) {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  padding: 1.5rem 2rem;
  border: none;
}

.availability-dialog :deep(.p-dialog-header-icon) {
  color: white;
}

.availability-content {
  height: calc(80vh - 120px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
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
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 10;
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
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.summary-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
  transition: opacity 0.3s ease;
  opacity: 0;
}

.summary-item:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
}

.summary-item:hover::before {
  opacity: 1;
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

/* Compact legend in controls bar */
.legend-inline {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.legend-items-compact {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.legend-item-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #4b5563;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(5px);
  transition: all 0.2s ease;
}

.legend-item-compact:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-item-compact .status-indicator.unavailable {
  background: linear-gradient(135deg, #ef4444, #dc2626) !important;
}

.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1);
  flex-shrink: 0;
  transition: all 0.2s ease;
  position: relative;
}

.status-indicator::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.5), transparent);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.availability-cell:hover .status-indicator::before {
  opacity: 1;
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
.status-indicator.unknown {
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
  opacity: 0.7;
}

.grid-container {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.grid-wrapper {
  border: 1px solid rgba(226, 232, 240, 0.6);
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.grid-wrapper:hover {
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
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
  min-width: 80px;
  padding: 1.25rem 0.75rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-weight: 700;
  color: #334155;
  text-align: center;
  position: relative;
  transition: all 0.2s ease;
  border-bottom: 2px solid #e2e8f0;
}

.day-header:hover {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  color: #0f172a;
  transform: translateY(-1px);
}

.day-header.weekend {
  background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
  color: #92400e;
}

.day-header.weekend-separator {
  border-left: 4px double #3b82f6;
  box-shadow: -2px 0 4px rgba(59, 130, 246, 0.3);
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
  padding: 0.5rem;
  text-align: center;
  vertical-align: middle;
  border-right: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  transition: all 0.2s ease;
  min-width: 80px;
  height: 60px;
}

.availability-cell.weekend-separator {
  border-left: 4px double #3b82f6;
  box-shadow: -2px 0 4px rgba(59, 130, 246, 0.2);
}

.availability-cell:hover {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  z-index: 5;
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
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-weight: 600;
  border-top: 2px solid #64748b;
  padding: 0.75rem 0.5rem;
  text-align: center;
  vertical-align: middle;
  border-right: 1px solid #cbd5e1;
}

.total-cell.weekend-separator {
  border-left: 4px double #3b82f6;
  box-shadow: -2px 0 4px rgba(59, 130, 246, 0.2);
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
