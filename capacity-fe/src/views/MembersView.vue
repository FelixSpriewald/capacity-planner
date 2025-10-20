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
                  icon="pi pi-trash"
                  class="p-button-text p-button-sm p-button-danger"
                  @click="confirmDeleteMember(member)"
                  v-tooltip="'Member löschen'"
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
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">Gesamt Members</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.active }}</div>
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

    <!-- Member Dialog -->
    <MemberForm
      :visible="showMemberDialog"
      :member="selectedMemberForEdit"
      :loading="dialogLoading"
      @update:visible="showMemberDialog = $event"
      @submit="handleMemberSubmit"
    />

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Button from 'primevue/button'
import Card from 'primevue/card'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'
import MemberForm from '@/components/forms/MemberForm.vue'
import { useMembersStore } from '@/stores/members'
import type { Member } from '@/types'

const membersStore = useMembersStore()
const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

// Dialog state
const showMemberDialog = ref(false)
const selectedMemberForEdit = ref<Member | null>(null)
const dialogLoading = ref(false)

// Computed from store
const loading = computed(() => membersStore.loading)
const members = computed(() => membersStore.members)
const stats = computed(() => membersStore.stats)

const createMember = () => {
  selectedMemberForEdit.value = null
  showMemberDialog.value = true
}

const viewMember = (member: Member) => {
  router.push(`/members/${member.member_id}`)
}

const editMember = (member: Member) => {
  selectedMemberForEdit.value = member
  showMemberDialog.value = true
}


const confirmDeleteMember = (member: Member) => {
  confirm.require({
    message: `Möchten Sie das Member "${member.name}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`,
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
      deleteMember(member)
    }
  })
}

const deleteMember = async (member: Member) => {
  try {
    await membersStore.deleteMember(member.member_id)
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: `Member "${member.name}" wurde gelöscht`,
      life: 3000
    })
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
  try {
    dialogLoading.value = true

    if (selectedMemberForEdit.value) {
      // Edit existing member (preserve active status)
      await membersStore.updateMember(selectedMemberForEdit.value.member_id, {
        ...memberData,
        active: selectedMemberForEdit.value.active
      })
      toast.add({
        severity: 'success',
        summary: 'Erfolgreich',
        detail: 'Member wurde aktualisiert',
        life: 3000
      })
    } else {
      // Create new member (automatically set as active)
      await membersStore.createMember({
        ...memberData,
        active: true
      })
      toast.add({
        severity: 'success',
        summary: 'Erfolgreich',
        detail: 'Neues Member wurde hinzugefügt',
        life: 3000
      })
    }

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

const formatEmploymentRatio = (ratio: number) => {
  return `${Math.round(ratio * 100)}%`
}

onMounted(async () => {
  // Load members from store (will use mock data if API not available)
  await membersStore.fetchMembers()
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
