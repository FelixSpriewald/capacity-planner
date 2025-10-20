<template>
  <div class="members-view">
    <div class="page-header">
      <h1 class="page-title">
        <i class="pi pi-users"></i>
        Team Members
      </h1>
      <Button
        label="Neues Mitglied"
        icon="pi pi-plus"
        @click="createMember"
        class="p-button-success"
      />
    </div>

    <div class="members-content">
      <Card>
        <template #content>
          <div v-if="loading" class="loading-state">
            <ProgressSpinner size="50px" />
            <p>Lade Team Members...</p>
          </div>

          <div v-else-if="members.length === 0" class="empty-state">
            <i class="pi pi-user-plus empty-icon"></i>
            <h3>Keine Team Members vorhanden</h3>
            <p>Füge dein erstes Team Member hinzu um zu beginnen</p>
            <Button
              label="Member hinzufügen"
              icon="pi pi-plus"
              @click="createMember"
              class="p-button-outlined"
            />
          </div>

          <div v-else class="members-grid">
            <div v-for="member in members" :key="member.member_id" class="member-card">
              <div class="member-header">
                <div class="member-avatar">
                  <i class="pi pi-user"></i>
                </div>
                <div class="member-info">
                  <h4 class="member-name">{{ member.name }}</h4>
                  <div class="member-details">
                    <div class="detail-item">
                      <i class="pi pi-clock"></i>
                      <span>{{ formatEmploymentRatio(member.employment_ratio) }}</span>
                    </div>
                    <div class="detail-item">
                      <i class="pi pi-map-marker"></i>
                      <span>{{ member.region_code }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="member-status">
                <Tag
                  :value="member.active ? 'Aktiv' : 'Inaktiv'"
                  :severity="member.active ? 'success' : 'secondary'"
                />
              </div>

              <div class="member-actions">
                <Button
                  icon="pi pi-eye"
                  class="p-button-text p-button-sm"
                  @click="viewMember(member)"
                  v-tooltip="'Member anzeigen'"
                />
                <Button
                  icon="pi pi-pencil"
                  class="p-button-text p-button-sm"
                  @click="editMember(member)"
                  v-tooltip="'Member bearbeiten'"
                />
                <Button
                  icon="pi pi-calendar"
                  class="p-button-text p-button-sm"
                  @click="managePTO(member)"
                  v-tooltip="'PTO verwalten'"
                />
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Team Statistics -->
      <div class="stats-section">
        <h3>Team Statistiken</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-users"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalMembers }}</div>
              <div class="stat-label">Gesamt Members</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.activeMembers }}</div>
              <div class="stat-label">Aktive Members</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-clock"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalCapacity }}h</div>
              <div class="stat-label">Wochenkapazität</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-globe"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.uniqueRegions }}</div>
              <div class="stat-label">Regionen</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

interface Member {
  member_id: number
  name: string
  employment_ratio: number
  region_code: string
  active: boolean
}

const loading = ref(true)
const members = ref<Member[]>([])

const createMember = () => {
  console.log('Neues Member erstellen...')
}

const viewMember = (member: Member) => {
  console.log('Member anzeigen:', member.name)
}

const editMember = (member: Member) => {
  console.log('Member bearbeiten:', member.name)
}

const managePTO = (member: Member) => {
  console.log('PTO verwalten für:', member.name)
}

const formatEmploymentRatio = (ratio: number) => {
  return `${Math.round(ratio * 100)}%`
}

const stats = computed(() => {
  const totalMembers = members.value.length
  const activeMembers = members.value.filter((m) => m.active).length
  const totalCapacity = members.value
    .filter((m) => m.active)
    .reduce((sum, m) => sum + m.employment_ratio * 40, 0) // 40h Vollzeit
  const uniqueRegions = new Set(members.value.map((m) => m.region_code)).size

  return {
    totalMembers,
    activeMembers,
    totalCapacity: Math.round(totalCapacity),
    uniqueRegions,
  }
})

onMounted(async () => {
  // Simuliere API-Call
  setTimeout(() => {
    members.value = [
      {
        member_id: 1,
        name: 'Alice Schmidt',
        employment_ratio: 1,
        region_code: 'DE-NW',
        active: true,
      },
      {
        member_id: 2,
        name: 'Bogdan Petrov',
        employment_ratio: 1,
        region_code: 'UA',
        active: true,
      },
    ]
    loading.value = false
  }, 800)
})
</script>

<style scoped>
.members-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.members-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #95a5a6;
  margin-bottom: 2rem;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.member-card {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s ease-in-out;
  background: white;
}

.member-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
  transform: translateY(-2px);
}

.member-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.member-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.member-info {
  flex: 1;
}

.member-name {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.detail-item .pi {
  width: 14px;
  font-size: 0.8rem;
}

.member-status {
  margin-bottom: 1rem;
}

.member-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.stats-section {
  margin-top: 2rem;
}

.stats-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 50px;
  height: 50px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3498db;
  font-size: 1.2rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
