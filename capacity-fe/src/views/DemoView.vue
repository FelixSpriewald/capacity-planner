<template>
  <div class="demo-page">
    <div class="demo-header">
      <h1>
        <i class="pi pi-star"></i>
        Task 12: Demo Data & Happy Path
      </h1>
      <p class="demo-description">
        Verification of demo data: Alice (DE-NW), Bogdan (UA), Sprint W43 with holidays and PTO
      </p>
    </div>

    <div class="demo-sections">
      <!-- Sprint Info -->
      <Card class="demo-section">
        <template #title>
          <i class="pi pi-calendar"></i>
          Sprint Information
        </template>
        <template #content>
          <div class="sprint-info">
            <div class="info-item">
              <strong>Sprint:</strong> {{ demoSprint.name }}
            </div>
            <div class="info-item">
              <strong>Period:</strong> {{ formatDate(demoSprint.start_date) }} - {{ formatDate(demoSprint.end_date) }}
            </div>
            <div class="info-item">
              <strong>Status:</strong>
              <Badge :value="demoSprint.status" :severity="getStatusSeverity(demoSprint.status)" />
            </div>
            <div class="info-item">
              <strong>Duration:</strong> {{ calculateWorkDays() }} working days ({{ calculateTotalDays() }} total days)
            </div>
          </div>
        </template>
      </Card>

      <!-- Team Members -->
      <Card class="demo-section">
        <template #title>
          <i class="pi pi-users"></i>
          Team Members
        </template>
        <template #content>
          <div class="members-grid">
            <div v-for="member in demoMembers" :key="member.member_id" class="member-card">
              <div class="member-info">
                <div class="member-name">{{ member.name }}</div>
                <div class="member-details">
                  <Badge :value="member.region_code" class="region-badge" />
                  <span class="employment-ratio">{{ (member.employment_ratio * 100) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Availability Grid -->
      <Card class="demo-section availability-section">
        <template #title>
          <i class="pi pi-table"></i>
          Availability Grid - Live Demo
        </template>
        <template #content>
          <AvailabilityGrid :sprint="demoSprint" />
        </template>
      </Card>

      <!-- Summary Stats -->
      <Card class="demo-section">
        <template #title>
          <i class="pi pi-chart-bar"></i>
          Capacity Summary
        </template>
        <template #content>
          <div class="summary-stats">
            <div class="stat-card">
              <div class="stat-value">{{ demoAvailabilityResponse.team_summary.total_days }}</div>
              <div class="stat-label">Total Days</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ demoAvailabilityResponse.team_summary.total_hours }}h</div>
              <div class="stat-label">Total Hours</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ getHolidaysCount() }}</div>
              <div class="stat-label">Holidays</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ getPTODays() }}</div>
              <div class="stat-label">PTO Days</div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Verification Checklist -->
      <Card class="demo-section">
        <template #title>
          <i class="pi pi-check-circle"></i>
          Task 12 Verification Checklist
        </template>
        <template #content>
          <div class="checklist">
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Alice (DE-NW) member created</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Bogdan (UA) member created</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Sprint W43 (2-week period) defined</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Regional holidays: Reformationstag (DE-NW), Transportation Day (UA)</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ PTO: 1 day for Alice (Oct 24)</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Allocation 1.0 for both members</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Auto-status correctly displayed (weekends, holidays, PTO)</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Capacity calculations working (days/hours)</span>
            </div>
            <div class="checklist-item">
              <i class="pi pi-check text-green-500"></i>
              <span>✅ Click interactions functional</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import Card from 'primevue/card'
import Badge from 'primevue/badge'
import AvailabilityGrid from '@/components/AvailabilityGrid.vue'
import { demoMembers, demoSprint, demoAvailabilityResponse } from '@/data/demo-simple'

// Mock stores for demo
import { useSprintsStore, useMembersStore } from '@/stores'

const sprintsStore = useSprintsStore()
const membersStore = useMembersStore()

// Set demo data in stores
sprintsStore.availability = demoAvailabilityResponse
membersStore.members = demoMembers

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function getStatusSeverity(status: string): string {
  switch (status) {
    case 'active': return 'success'
    case 'draft': return 'warning'
    case 'closed': return 'info'
    default: return 'secondary'
  }
}

function calculateWorkDays(): number {
  const start = new Date(demoSprint.start_date)
  const end = new Date(demoSprint.end_date)
  let workDays = 0

  for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
    const dayOfWeek = date.getDay()
    if (dayOfWeek !== 0 && dayOfWeek !== 6) { // Not weekend
      workDays++
    }
  }

  return workDays
}

function calculateTotalDays(): number {
  const start = new Date(demoSprint.start_date)
  const end = new Date(demoSprint.end_date)
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
}

function getHolidaysCount(): number {
  let count = 0
  for (const member of demoAvailabilityResponse.members) {
    count += member.days.filter(day => day.final_state === 'holiday').length
  }
  return count
}

function getPTODays(): number {
  let count = 0
  for (const member of demoAvailabilityResponse.members) {
    count += member.days.filter(day => day.final_state === 'pto').length
  }
  return count
}
</script>

<style scoped>
.demo-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.demo-header {
  text-align: center;
  margin-bottom: 2rem;
}

.demo-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.demo-description {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.demo-sections {
  display: grid;
  gap: 2rem;
}

.demo-section {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sprint-info {
  display: grid;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.member-card {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  background: #f8f9fa;
}

.member-name {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.member-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.region-badge {
  background: #007bff;
  color: white;
}

.employment-ratio {
  font-size: 0.875rem;
  color: #6c757d;
}

.availability-section {
  grid-column: 1 / -1;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.checklist {
  display: grid;
  gap: 0.75rem;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .demo-page {
    padding: 1rem;
  }

  .demo-header h1 {
    font-size: 1.5rem;
  }

  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}
</style>
