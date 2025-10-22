<template>
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
        <div class="days">{{ teamTotalDays }}d</div>
      </div>
    </td>
  </tr>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  visibleDays: Array<{
    date: string
    dayName: string
    displayDate: string
    isWeekend: boolean
    showWeekendSeparator?: boolean | null
  }>
  availability: {
    members?: Array<{
      allocation?: number
      days?: Array<{
        day?: string
        date?: string
        dateString?: string
        day_date?: string
        final_state?: string
      }>
    }>
    sum_days_team?: number
    team_summary?: {
      total_days?: number
    }
  }
}

const props = defineProps<Props>()

// Computed
const teamTotalDays = computed(() => {
  return props.availability.sum_days_team || props.availability.team_summary?.total_days || 0
})

// Optimized: Pre-compute day totals once instead of O(n²) per render
const dayTotalsMap = computed(() => {
  if (!props.availability?.members) return new Map<string, string>()

  const totalsMap = new Map<string, number>()

  // Build map once with O(n) complexity
  props.availability.members.forEach(member => {
    member.days?.forEach(day => {
      const dayDate = day.day || day.date || day.dateString || day.day_date
      if (!dayDate) return

      const allocation = Number(member.allocation) || 1
      const currentTotal = totalsMap.get(dayDate) || 0

      if (day.final_state === 'available') {
        totalsMap.set(dayDate, currentTotal + allocation)
      } else if (day.final_state === 'half') {
        totalsMap.set(dayDate, currentTotal + allocation * 0.5)
      }
    })
  })

  // Convert to formatted strings
  const formattedMap = new Map<string, string>()
  totalsMap.forEach((total, date) => {
    formattedMap.set(date, Number(total).toFixed(1))
  })

  return formattedMap
})

// Methods - now O(1) lookup
const getDayTotal = (date: string) => {
  return dayTotalsMap.value.get(date) || '0'
}
</script>
