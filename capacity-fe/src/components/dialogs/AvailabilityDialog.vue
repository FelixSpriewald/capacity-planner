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
        <ControlsBar
          :member-count="availability.members.length"
          :visible-days-count="visibleDays.length"
          :total-days="availability.sum_days_team || availability.team_summary?.total_days || 0"
        />

        <!-- Availability Grid -->
        <div class="grid-container">
          <div class="grid-wrapper">
            <table class="availability-grid">
              <!-- Header -->
              <GridHeader :visible-days="visibleDays" />

              <!-- Body -->
              <tbody>
                <MemberRow
                  v-for="member in availability.members"
                  :key="member.member_id"
                  :member="member"
                  :visible-days="visibleDays"
                  :get-member-day="getMemberDay"
                  :get-status-class="getStatusClass"
                  :get-tooltip="getTooltip"
                  :handle-cell-click="handleCellClick"
                />

                <!-- Team Totals -->
                <SummaryItems
                  :visible-days="visibleDays"
                  :availability="availability"
                />
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
import ControlsBar from '../ControlsBar.vue'
import GridHeader from '../GridHeader.vue'
import MemberRow from '../MemberRow.vue'
import SummaryItems from '../SummaryItems.vue'

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

// Type-safe day interface
interface DayWithFlexibleDateField {
  day?: string
  date?: string
  dateString?: string
  day_date?: string
  final_state?: string
  auto_status?: string
  override_state?: string
}

// Helper function to get date field safely
const getDateField = (dayObj: DayWithFlexibleDateField): string | undefined => {
  return dayObj.day || dayObj.date || dayObj.dateString || dayObj.day_date
}

// Computed
const visibleDays = computed(() => {
  if (!props.availability?.members?.length) return []

  const firstMember = props.availability.members[0]
  if (!firstMember?.days?.length) return []

  return firstMember.days
    .filter(day => {
      const dateField = getDateField(day as DayWithFlexibleDateField)
      return dateField && !isWeekend(dateField)
    })
    .map((day, index, filteredDays) => {
      const dateField = getDateField(day as DayWithFlexibleDateField)
      if (!dateField) return null // Skip invalid dates

      const previousDay = index > 0 ? filteredDays[index - 1] : null
      const previousDateField = previousDay ? getDateField(previousDay as DayWithFlexibleDateField) : null
      const showWeekendSeparator = previousDay && previousDateField ? hasWeekendBetween(previousDateField, dateField) : null

      return {
        date: dateField,
        dayName: getDayName(dateField),
        displayDate: getDisplayDate(dateField),
        isWeekend: isWeekend(dateField),
        showWeekendSeparator
      }
    })
    .filter((day): day is NonNullable<typeof day> => day !== null) // Type guard to filter out nulls
})

// Utility functions
const isWeekend = (dateString: string) => {
  const date = new Date(dateString)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 0 || dayOfWeek === 6
}

const getDayName = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString + 'T00:00:00')
  if (isNaN(date.getTime())) {
    return dateString
  }
  return date.toLocaleDateString('de-DE', { weekday: 'short' })
}

const getDisplayDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString + 'T00:00:00')
  if (isNaN(date.getTime())) {
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
  return diffDays > 1
}

const getMemberDay = (member: any, date: string) => {
  return member.days?.find((d: DayWithFlexibleDateField) => {
    const dayDate = getDateField(d)
    return dayDate === date
  })
}

const getStatusClass = (day: DayAvailability | null) => {
  if (!day) return 'unknown'

  const state = day.final_state
  const overrideState = day.override_state

  if (overrideState !== null && overrideState !== undefined) {
    switch (overrideState) {
      case 'available':
        return 'available'
      case 'half':
        return 'half'
      case 'out':
        return 'unavailable'
      default:
        return 'unavailable'
    }
  }

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

const getTooltip = (memberName: string, memberDay: DayWithFlexibleDateField) => {
  const dayDate = getDateField(memberDay)
  let formattedDate = 'Unbekanntes Datum'

  if (dayDate) {
    const date = new Date(dayDate + 'T00:00:00')
    if (!isNaN(date.getTime())) {
      formattedDate = date.toLocaleDateString('de-DE')
    } else {
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

  const stateLabel = stateLabels[memberDay.final_state || 'unknown'] || `Unbekannt (${memberDay.final_state})`
  const memberDisplayName = memberName || 'Unbekanntes Mitglied'
  return `${memberDisplayName} - ${formattedDate}: ${stateLabel}`
}

// Event handlers
const handleCellClick = (memberId: number, date: string, day: DayAvailability | null) => {
  if (!day) return
  // Don't allow editing weekends or holidays
  if (day.final_state === 'weekend' || day.final_state === 'holiday') {
    return
  }

  emit('toggle-availability', memberId, date, day)
}
</script>

<style>
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
  table-layout: fixed;
  display: table;
}

.availability-grid th,
.availability-grid td {
  padding: 0;
  border: 1px solid #f3f4f6;
  text-align: center;
  vertical-align: middle;
  transition: all 0.2s ease;
}

.member-row {
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.member-row:hover {
  background: rgba(248, 250, 252, 0.8);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.member-cell {
  min-width: 220px;
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  position: sticky;
  left: 0;
  z-index: 10;
  border-right: 3px solid #e2e8f0;
  font-weight: 500;
  box-shadow: 2px 0 4px rgba(0,0,0,0.05);
}

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

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem;
}

.member-name {
  font-weight: 700;
  font-size: 1rem;
  color: #1f2937;
  line-height: 1.3;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  text-align: center;
  transition: all 0.2s ease;
}

.member-name:hover {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.member-allocation {
  font-size: 0.875rem;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  transition: all 0.2s ease;
  min-height: 36px;
}

.member-allocation:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.availability-cell {
  position: relative;
  text-align: center;
  padding: 1rem 0.75rem;
  border-right: 1px solid rgba(226, 232, 240, 0.3);
  transition: all 0.2s ease;
  cursor: default;
  min-height: 60px;
  min-width: 80px;
  vertical-align: middle;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.availability-cell.weekend-separator {
  border-left: 4px double #3b82f6;
  box-shadow: -2px 0 4px rgba(59, 130, 246, 0.2);
}

.availability-cell:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.availability-cell.clickable {
  cursor: pointer;
}

.availability-cell.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.2), inset 0 0 0 2px rgba(255, 255, 255, 0.3);
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

.status-indicator,
.status-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
  transition: all 0.3s ease;
  position: relative;
  display: block;
  flex-shrink: 0;

}

.status-indicator,
.status-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
  transition: all 0.3s ease;
  position: relative;
}

.availability-cell:hover .status-indicator,
.availability-cell:hover .status-dot {
  transform: scale(1.15);
  box-shadow: 0 6px 12px rgba(0,0,0,0.2), 0 6px 12px rgba(0,0,0,0.25);
}

.availability-cell.available {
  background: linear-gradient(135deg, #10b981, #059669) !important;
  color: white;
  font-weight: 600;
}

.availability-cell.half {
  background: linear-gradient(135deg, #f59e0b, #fbbf24) !important;
  color: white;
  font-weight: 600;
}

.availability-cell.unavailable {
  background: linear-gradient(135deg, #ef4444, #dc2626) !important;
  color: white;
  font-weight: 600;
}

.availability-cell.weekend {
  background: linear-gradient(135deg, #9ca3af, #6b7280) !important;
  color: white;
  font-weight: 600;
}

.availability-cell.holiday {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
  color: white;
  font-weight: 600;
}

.availability-cell.unknown {
  background: linear-gradient(135deg, #d1d5db, #9ca3af) !important;
  color: #4b5563;
  font-weight: 600;
}

.status-indicator.available,
.status-dot.available {
  background: linear-gradient(135deg, #10b981, #059669) !important;
}

.status-indicator.half,
.status-dot.half {
  background: linear-gradient(90deg, #f59e0b 50%, #fbbf24 50%) !important;
}

.status-indicator.unavailable,
.status-dot.unavailable {
  background: linear-gradient(135deg, #ef4444, #dc2626) !important;
}

.status-indicator.weekend,
.status-dot.weekend {
  background: linear-gradient(135deg, #9ca3af, #6b7280) !important;
}

.status-indicator.holiday,
.status-dot.holiday {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
}

.status-indicator.unknown,
.status-dot.unknown {
  background: linear-gradient(135deg, #d1d5db, #9ca3af) !important;
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
  .member-cell {
    min-width: 140px;
    padding: 0.75rem;
  }

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
