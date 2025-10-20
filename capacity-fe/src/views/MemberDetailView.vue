<template>
  <div class="member-detail-view">
    <!-- Navigation Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/members" class="breadcrumb-link">
        <i class="pi pi-arrow-left"></i>
        Zurück zu Members
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner size="50px" />
      <p>Lade Member-Details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <i class="pi pi-exclamation-triangle error-icon"></i>
      <h3>Fehler beim Laden</h3>
      <p>{{ error }}</p>
      <Button
        label="Erneut versuchen"
        icon="pi pi-refresh"
        @click="loadMember"
        class="p-button-outlined"
      />
    </div>

    <!-- Member Detail Content -->
    <div v-else-if="member" class="member-detail-content">
      <!-- Header Section -->
      <div class="member-header">
        <div class="member-info">
          <div class="member-avatar-large">
            <i class="pi pi-user"></i>
          </div>
          <div class="member-details">
            <div class="member-title">
              <h1 class="member-name">{{ member.name }}</h1>
            </div>
            <div class="member-subtitle">
              <div class="detail-item">
                <i class="pi pi-clock"></i>
                <span>{{ formatEmploymentRatio(member.employment_ratio) }} Arbeitszeit</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-map-marker"></i>
                <span>{{ getRegionName(member.region_code) }}</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-calendar"></i>
                <span>Member ID: {{ member.member_id }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="member-actions">
          <Button
            label="Bearbeiten"
            icon="pi pi-pencil"
            @click="editMember"
            class="p-button-outlined"
          />
          <Button
            label="Löschen"
            icon="pi pi-trash"
            @click="confirmDeleteMember"
            severity="danger"
            class="p-button-outlined"
          />
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-section">
        <h3>Kapazitäts-Übersicht</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-clock"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ weeklyHours }}h</div>
              <div class="stat-label">Wochenkapazität</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-calendar"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyHours }}h</div>
              <div class="stat-label">Monatskapazität (ca.)</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-chart-line"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatEmploymentRatio(member.employment_ratio) }}</div>
              <div class="stat-label">Arbeitszeit-Anteil</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-globe"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ member.region_code }}</div>
              <div class="stat-label">Region</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity (Placeholder) -->
      <div class="activity-section">
        <h3>Letzte Aktivitäten</h3>
        <Card>
          <template #content>
            <div class="empty-state">
              <i class="pi pi-history empty-icon"></i>
              <h4>Noch keine Aktivitäten</h4>
              <p>Sprint-Teilnahmen und PTO-Einträge werden hier angezeigt</p>
            </div>
          </template>
        </Card>
      </div>

      <!-- Sprint History (Placeholder) -->
      <div class="sprint-history-section">
        <h3>Sprint-Verlauf</h3>
        <Card>
          <template #content>
            <div class="empty-state">
              <i class="pi pi-calendar-times empty-icon"></i>
              <h4>Kein Sprint-Verlauf</h4>
              <p>Vergangene und geplante Sprint-Teilnahmen werden hier angezeigt</p>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Member Not Found -->
    <div v-else class="not-found-state">
      <i class="pi pi-user-times not-found-icon"></i>
      <h3>Member nicht gefunden</h3>
      <p>Das gesuchte Member existiert nicht oder wurde entfernt</p>
      <router-link to="/members">
        <Button
          label="Zurück zu Members"
          icon="pi pi-arrow-left"
          class="p-button-outlined"
        />
      </router-link>
    </div>

    <!-- Member Form Dialog -->
    <MemberForm
      :visible="showMemberDialog"
      :member="member"
      :loading="dialogLoading"
      @update:visible="showMemberDialog = $event"
      @submit="handleMemberSubmit"
    />

    <!-- Confirmation Dialogs -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Button from 'primevue/button'
import Card from 'primevue/card'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'
import MemberForm from '@/components/forms/MemberForm.vue'
import { useMembersStore } from '@/stores/members'
import type { Member } from '@/types'

const route = useRoute()
const router = useRouter()
const membersStore = useMembersStore()
const toast = useToast()
const confirm = useConfirm()

// State
const member = ref<Member | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const showMemberDialog = ref(false)
const dialogLoading = ref(false)

// Computed
const weeklyHours = computed(() => {
  if (!member.value) return 0
  return Math.round(member.value.employment_ratio * 40) // 40h Vollzeit
})

const monthlyHours = computed(() => {
  if (!member.value) return 0
  return Math.round(weeklyHours.value * 4.33) // Durchschnittlich 4.33 Wochen pro Monat
})

// Methods
const formatEmploymentRatio = (ratio: number) => {
  return `${Math.round(ratio * 100)}%`
}

const getRegionName = (regionCode: string) => {
  const regionMap: Record<string, string> = {
    'DE-NW': 'Deutschland - Nordrhein-Westfalen',
    'DE-BY': 'Deutschland - Bayern',
    'DE-BW': 'Deutschland - Baden-Württemberg',
    'DE-HE': 'Deutschland - Hessen',
    'DE-BE': 'Deutschland - Berlin',
    'AT': 'Österreich',
    'CH': 'Schweiz',
    'UA': 'Ukraine',
    'PL': 'Polen',
    'CZ': 'Tschechien'
  }
  return regionMap[regionCode] || regionCode
}

const loadMember = async () => {
  const memberId = Number.parseInt(route.params.id as string)
  if (Number.isNaN(memberId)) {
    error.value = 'Ungültige Member-ID'
    return
  }

  try {
    loading.value = true
    error.value = null
    member.value = await membersStore.fetchMember(memberId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Fehler beim Laden des Members'
    console.error('Failed to load member:', err)
  } finally {
    loading.value = false
  }
}

const editMember = () => {
  showMemberDialog.value = true
}


const confirmDeleteMember = () => {
  if (!member.value) return

  confirm.require({
    message: `Möchten Sie das Member "${member.value.name}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`,
    header: 'Member löschen',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Abbrechen',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Löschen',
      severity: 'danger'
    },
    accept: () => {
      deleteMember()
    }
  })
}

const deleteMember = async () => {
  if (!member.value) return

  try {
    await membersStore.deleteMember(member.value.member_id)
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: `Member "${member.value.name}" wurde gelöscht`,
      life: 3000
    })
    // Navigate back to members list
    router.push('/members')
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error instanceof Error ? error.message : 'Fehler beim Löschen des Members',
      life: 5000
    })
  }
}


const handleMemberSubmit = async (memberData: {
  name: string
  employment_ratio: number
  region_code: string
}) => {
  if (!member.value) return

  try {
    dialogLoading.value = true
    const updated = await membersStore.updateMember(member.value.member_id, {
      ...memberData,
      active: true // Always keep as active when updating
    })
    member.value = updated
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Member wurde aktualisiert',
      life: 3000
    })
    showMemberDialog.value = false
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error instanceof Error ? error.message : 'Unbekannter Fehler',
      life: 5000
    })
  } finally {
    dialogLoading.value = false
  }
}

onMounted(() => {
  loadMember()
})
</script>

<style scoped>
.member-detail-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.breadcrumb {
  margin-bottom: 2rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease-in-out;
}

.breadcrumb-link:hover {
  color: #2980b9;
}

.loading-state,
.error-state,
.not-found-state {
  text-align: center;
  padding: 4rem 2rem;
}

.error-icon,
.not-found-icon {
  font-size: 4rem;
  color: #e74c3c;
  margin-bottom: 1rem;
}

.not-found-icon {
  color: #95a5a6;
}

.member-detail-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.member-header {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.member-info {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  flex: 1;
}

.member-avatar-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  flex-shrink: 0;
}

.member-details {
  flex: 1;
}

.member-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.member-name {
  margin: 0;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 600;
}

.member-status-tag {
  font-size: 0.9rem;
}

.member-subtitle {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #7f8c8d;
  font-size: 1rem;
}

.detail-item .pi {
  width: 16px;
  font-size: 0.9rem;
  color: #3498db;
}

.member-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 150px;
}

.stats-section,
.activity-section,
.sprint-history-section {
  margin-top: 2rem;
}

.stats-section h3,
.activity-section h3,
.sprint-history-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.5rem;
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
  transition: box-shadow 0.2s ease-in-out;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: #f8f9fa;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3498db;
  font-size: 1.5rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 1rem;
}

.empty-state h4 {
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #95a5a6;
}

@media (max-width: 768px) {
  .member-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .member-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .member-actions {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    min-width: auto;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .member-detail-view {
    padding: 1rem;
  }
}
</style>