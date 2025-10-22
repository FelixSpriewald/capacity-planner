<template>
  <div class="sprint-info-dashboard">
    <div class="dashboard-cards">
      <!-- Working Days Card -->
      <div class="info-card">
        <div class="card-icon">
          <i class="pi pi-calendar"></i>
        </div>
        <div class="card-content">
          <div class="card-value">{{ workingDays }}</div>
          <div class="card-label">Working Days</div>
        </div>
      </div>

      <!-- Holidays Card -->
      <div class="info-card">
        <div class="card-icon">
          <i class="pi pi-star"></i>
        </div>
        <div class="card-content">
          <div class="card-value">{{ totalHolidays }}</div>
          <div class="card-label">Holidays</div>
          <div v-if="holidaysByRegion.length > 0" class="card-detail">
            <span v-for="(region, index) in holidaysByRegion" :key="region.region">
              {{ region.region }}: {{ region.count }}{{ index < holidaysByRegion.length - 1 ? ', ' : '' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Team Size Card -->
      <div class="info-card">
        <div class="card-icon">
          <i class="pi pi-users"></i>
        </div>
        <div class="card-content">
          <div class="card-value">{{ teamSize }}</div>
          <div class="card-label">Team Members</div>
          <div class="card-detail">{{ activeMembers }} active</div>
        </div>
      </div>

      <!-- Total Capacity Card -->
      <div class="info-card">
        <div class="card-icon">
          <i class="pi pi-clock"></i>
        </div>
        <div class="card-content">
          <div class="card-value">{{ totalCapacityHours }}h</div>
          <div class="card-label">Total Capacity</div>
          <div class="card-detail">{{ totalCapacityDays }} days</div>
        </div>
      </div>

      <!-- Available Capacity Card -->
      <div class="info-card">
        <div class="card-icon">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="card-content">
          <div class="card-value">{{ availableCapacityHours }}h</div>
          <div class="card-label">Available</div>
          <div class="card-detail">{{ availableCapacityDays }} days</div>
        </div>
      </div>

      <!-- Efficiency Card -->
      <div class="info-card">
        <div class="card-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div class="card-content">
          <div class="card-value">{{ efficiency }}%</div>
          <div class="card-label">Efficiency</div>
          <div class="card-detail">available / total</div>
        </div>
      </div>
    </div>

    <!-- Warnings Section -->
    <div v-if="warnings.length > 0" class="warnings-section">
      <h4 class="warnings-title">
        <i class="pi pi-exclamation-triangle"></i>
        Warnings & Notifications
      </h4>
      <div class="warnings-list">
        <div
          v-for="(warning, index) in warnings"
          :key="index"
          class="warning-item"
          :class="`warning-${warning.type}`"
        >
          <i :class="warning.icon"></i>
          <span>{{ warning.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Sprint, AvailabilityResponse, Member } from '@/types'

interface Props {
  sprint?: Sprint | null
  availability?: AvailabilityResponse | null
  members?: Member[]
}

interface Warning {
  type: 'error' | 'warning' | 'info'
  icon: string
  message: string
}

const props = defineProps<Props>()

// Use backend-calculated working days
const workingDays = computed(() => {
  return props.availability?.working_days || 0
})

// Use backend-calculated holidays by region
const holidaysByRegion = computed(() => {
  return props.availability?.holidays_by_region || []
})

const totalHolidays = computed(() => {
  return holidaysByRegion.value.reduce((sum, region) => sum + region.count, 0)
})

// Team information
const teamSize = computed(() => {
  return props.availability?.members.length || 0
})

const activeMembers = computed(() => {
  if (!props.members) return 0
  return props.members.filter(m => m.active).length
})

// Use backend-calculated capacity values
const totalCapacityHours = computed(() => {
  return props.availability?.team_summary?.total_hours || 0
})

const totalCapacityDays = computed(() => {
  return props.availability?.team_summary?.total_days || 0
})

const availableCapacityHours = computed(() => {
  return props.availability?.available_capacity_hours || 0
})

const availableCapacityDays = computed(() => {
  return props.availability?.available_capacity_days || 0
})

const efficiency = computed(() => {
  return props.availability?.efficiency_percentage || 0
})

// Warnings and notifications
const warnings = computed((): Warning[] => {
  const warningList: Warning[] = []

  if (!props.availability || !props.members) return warningList

  // Check for members without region code
  const membersWithoutRegion = props.members.filter(m =>
    m.active && !m.region_code &&
    props.availability!.members.some(ma => ma.member_id === m.member_id)
  )

  if (membersWithoutRegion.length > 0) {
    warningList.push({
      type: 'warning',
      icon: 'pi pi-map-marker',
      message: `${membersWithoutRegion.length} member(s) without region - holidays will be ignored`
    })
  }

  // Check for overrides on holidays/PTO
  let overrideWarnings = 0
  for (const member of props.availability.members) {
    for (const day of member.days) {
      if (day.override_state && (day.auto_status === 'holiday' || day.auto_status === 'pto')) {
        overrideWarnings++
      }
    }
  }

  if (overrideWarnings > 0) {
    warningList.push({
      type: 'warning',
      icon: 'pi pi-exclamation-triangle',
      message: `${overrideWarnings} override(s) on holidays or PTO days`
    })
  }

  // Check for low efficiency
  if (efficiency.value < 70 && efficiency.value > 0) {
    warningList.push({
      type: 'warning',
      icon: 'pi pi-chart-line',
      message: `Low team efficiency: ${efficiency.value}% available capacity`
    })
  }

  // Check for inactive members in roster
  const inactiveInRoster = props.members.filter(m =>
    !m.active && props.availability!.members.some(ma => ma.member_id === m.member_id)
  )

  if (inactiveInRoster.length > 0) {
    warningList.push({
      type: 'info',
      icon: 'pi pi-info-circle',
      message: `${inactiveInRoster.length} inactive member(s) in sprint roster`
    })
  }

  return warningList
})

// Helper functions removed - now using backend calculations
</script>

<style scoped>
.sprint-info-dashboard {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #3498db;
  transition: all 0.2s ease;
}

.info-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 40px;
  height: 40px;
  background: #3498db;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 1rem;
  font-size: 1.1rem;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.card-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-detail {
  font-size: 0.75rem;
  color: #95a5a6;
  margin-top: 0.25rem;
}

/* Specific card colors */
.info-card:nth-child(1) .card-icon { background: #3498db; }
.info-card:nth-child(1) { border-left-color: #3498db; }

.info-card:nth-child(2) .card-icon { background: #e74c3c; }
.info-card:nth-child(2) { border-left-color: #e74c3c; }

.info-card:nth-child(3) .card-icon { background: #9b59b6; }
.info-card:nth-child(3) { border-left-color: #9b59b6; }

.info-card:nth-child(4) .card-icon { background: #f39c12; }
.info-card:nth-child(4) { border-left-color: #f39c12; }

.info-card:nth-child(5) .card-icon { background: #27ae60; }
.info-card:nth-child(5) { border-left-color: #27ae60; }

.info-card:nth-child(6) .card-icon { background: #2ecc71; }
.info-card:nth-child(6) { border-left-color: #2ecc71; }

.warnings-section {
  border-top: 1px solid #e9ecef;
  padding-top: 1.5rem;
}

.warnings-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.warnings-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.warning-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
}

.warning-error {
  background: #fee;
  color: #c53030;
  border-left: 4px solid #e53e3e;
}

.warning-warning {
  background: #fffaf0;
  color: #b7791f;
  border-left: 4px solid #f6ad55;
}

.warning-info {
  background: #f0f8ff;
  color: #2c5282;
  border-left: 4px solid #4299e1;
}

@media (max-width: 768px) {
  .dashboard-cards {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .info-card {
    flex-direction: column;
    text-align: center;
  }

  .card-icon {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
}
</style>
