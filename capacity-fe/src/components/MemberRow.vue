<template>
  <tr class="member-row">
    <td class="member-cell">
      <div class="member-info">
        <div class="member-name">{{ member.member_name || member.name || `Member ${member.member_id}` }}</div>
        <div class="member-allocation">{{ member.allocation_percentage || Math.round((member.allocation || 1) * 100) }}%</div>
      </div>
    </td>

    <td
      v-for="day in visibleDays"
      :key="`${member.member_id}-${day.date}`"
      class="availability-cell"
      :class="{
        'weekend': day.isWeekend,
        'weekend-separator': day.showWeekendSeparator,
        'clickable': getMemberDay(member, day.date)?.final_state !== 'weekend' && getMemberDay(member, day.date)?.final_state !== 'holiday',
        [getMemberDay(member, day.date) ? getStatusClass(getMemberDay(member, day.date)) : 'unknown']: true
      }"
      @click="getMemberDay(member, day.date) && handleCellClick(member.member_id, day.date, getMemberDay(member, day.date))"
      :title="getMemberDay(member, day.date) ? getTooltip(member.member_name || member.name || `Member ${member.member_id}`, getMemberDay(member, day.date)) : ''"
    >
    </td>

    <td class="summary-cell">
      <div class="member-summary">
        <div class="days">{{ member.sum_days || member.summary?.total_days || 0 }}d</div>
      </div>
    </td>
  </tr>
</template>

<script setup lang="ts">
// Props
interface Props {
  member: any
  visibleDays: Array<{
    date: string
    dayName: string
    displayDate: string
    isWeekend: boolean
    showWeekendSeparator?: boolean | null
  }>
  getMemberDay: (member: any, date: string) => any
  getStatusClass: (memberDay: any) => string
  getTooltip: (memberName: string, memberDay: any) => string
  handleCellClick: (memberId: any, date: string, memberDay: any) => void
}

const props = defineProps<Props>()
</script>

<style scoped>
/* MemberRow-specific styles only */
.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.member-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.member-allocation {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 500;
}

.member-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.days {
  font-weight: 700;
  color: #1e293b;
  font-size: 1rem;
}
</style>
