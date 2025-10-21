<template>
  <div class="controls-bar">
    <div class="filters">
      <!-- Wochenenden werden automatisch ausgeblendet -->
    </div>

    <StatusLegend />

    <div class="summary">
      <div class="summary-item">
        <i class="pi pi-users"></i>
        <span>{{ memberCount }} Mitglieder</span>
      </div>
      <div class="summary-item">
        <i class="pi pi-calendar"></i>
        <span>{{ visibleDaysCount }} Tage</span>
      </div>
      <div class="summary-item">
        <i class="pi pi-calendar"></i>
        <span>{{ totalDays }} Gesamt-Tage</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import StatusLegend from './StatusLegend.vue'

// Props
interface Props {
  memberCount: number
  visibleDaysCount: number
  totalDays: number
}

withDefaults(defineProps<Props>(), {
  memberCount: 0,
  visibleDaysCount: 0,
  totalDays: 0
})
</script>

<style scoped>
.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.summary {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #475569;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  backdrop-filter: blur(5px);
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.summary-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-item i {
  color: #6366f1;
  font-size: 1rem;
}
</style>