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

// Methods
const getDayTotal = (date: string) => {
  if (!props.availability?.members) return '0'

  let total = 0
  props.availability.members.forEach(member => {
    // Handle the actual data structure - check multiple possible date fields
    const day = member.days?.find(d => {
      const dayDate = d.day || d.date || d.dateString || d.day_date
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
</script>