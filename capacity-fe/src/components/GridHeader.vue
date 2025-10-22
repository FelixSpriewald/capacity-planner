<template>
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
</template>

<script setup lang="ts">
// Props
interface Props {
  visibleDays: Array<{
    date: string
    dayName: string
    displayDate: string
    isWeekend: boolean
    showWeekendSeparator?: boolean | null
  }>
}

defineProps<Props>()
</script>

<style scoped>
.member-header,
.day-header,
.summary-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  color: #1e293b;
  font-weight: 700;
  text-align: center;
  padding: 1rem 0.75rem;
  border-bottom: 2px solid #cbd5e1;
  position: sticky;
  top: 0;
  z-index: 20;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.member-header {
  text-align: left;
  min-width: 200px;
  max-width: 200px;
  width: 200px;
  left: 0;
  z-index: 21;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border-right: 2px solid #cbd5e1;
}

.day-header {
  min-width: 80px;
  font-size: 0.75rem;
  position: relative;
}

.day-header.weekend {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #64748b;
}

.day-header.weekend-separator {
  border-left: 4px solid #3b82f6;
  box-shadow: -2px 0 0 #3b82f6, 0 2px 4px rgba(0, 0, 0, 0.1);
}

.day-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.day-name {
  font-weight: 600;
  font-size: 0.7rem;
  opacity: 0.8;
}

.day-date {
  font-weight: 700;
  font-size: 0.8rem;
}

.summary-header {
  min-width: 80px;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border-left: 2px solid #cbd5e1;
  position: sticky;
  right: 0;
  z-index: 21;
}

/* Responsive styles */
@media (max-width: 768px) {
  .member-header {
    min-width: 140px;
    max-width: 140px;
    width: 140px;
    padding: 0.75rem;
  }

  .day-header {
    min-width: 60px;
    padding: 0.5rem 0.25rem;
  }

  .day-name {
    font-size: 0.6rem;
  }

  .day-date {
    font-size: 0.7rem;
  }

  .summary-header {
    min-width: 60px;
    padding: 0.75rem 0.25rem;
  }
}
</style>
