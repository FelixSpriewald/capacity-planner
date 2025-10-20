<template>
  <Dialog
    :visible="visible"
    modal
    :header="`Team Roster - ${sprint?.name || 'Sprint'}`"
    :style="{ width: '800px' }"
    :closable="true"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="roster-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <ProgressSpinner size="50px" />
        <p>Lade Team Roster...</p>
      </div>

      <!-- Main Content -->
      <div v-else class="roster-main">
        <!-- Current Team Members -->
        <div class="current-team">
          <div class="section-header">
            <h3>
              <i class="pi pi-users"></i>
              Aktuelle Team-Mitglieder
            </h3>
            <Button
              label="Member hinzufügen"
              icon="pi pi-plus"
              @click="showAddMember = true"
              class="p-button-success p-button-sm"
            />
          </div>

          <!-- Empty State -->
          <div v-if="roster.length === 0" class="empty-state">
            <i class="pi pi-users empty-icon"></i>
            <h4>Keine Team-Mitglieder zugeordnet</h4>
            <p>Füge Members zu diesem Sprint hinzu um zu beginnen</p>
          </div>

          <!-- Team Members List -->
          <div v-else class="team-members">
            <Card
              v-for="member in roster"
              :key="member.member_id"
              class="member-card"
            >
              <template #content>
                <div class="member-info">
                  <div class="member-header">
                    <h4>{{ member.member_name || 'Unbekannt' }}</h4>
                    <Button
                      icon="pi pi-trash"
                      class="p-button-text p-button-sm p-button-danger"
                      @click.stop.prevent="confirmRemoveMember(member)"
                      v-tooltip="'Member entfernen'"
                    />
                  </div>

                  <div class="member-details">
                    <!-- Allocation -->
                    <div class="allocation-section">
                      <div class="allocation-label">
                        <strong>Allocation:</strong> {{ Math.round(member.allocation * 100) }}%
                      </div>
                      <Slider
                        v-model="member.allocation"
                        :min="0.1"
                        :max="1.0"
                        :step="0.1"
                        @change="updateMember(member)"
                        class="allocation-slider"
                      />
                    </div>

                    <!-- Assignment Dates -->
                    <div class="assignment-dates">
                      <div class="date-field">
                        <label><strong>Assignment von:</strong></label>
                        <Calendar
                          v-model="member.assignment_from_date"
                          dateFormat="dd.mm.yy"
                          :minDate="sprintStartDate"
                          :maxDate="sprintEndDate"
                          placeholder="Gesamter Sprint"
                          showButtonBar
                          @date-select="updateMember(member)"
                        />
                      </div>
                      <div class="date-field">
                        <label><strong>Assignment bis:</strong></label>
                        <Calendar
                          v-model="member.assignment_to_date"
                          dateFormat="dd.mm.yy"
                          :minDate="sprintStartDate"
                          :maxDate="sprintEndDate"
                          placeholder="Gesamter Sprint"
                          showButtonBar
                          @date-select="updateMember(member)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Member Dialog -->
    <Dialog
      v-model:visible="showAddMember"
      modal
      header="Member hinzufügen"
      :style="{ width: '500px' }"
    >
      <div class="add-member-content">
        <div class="form-field">
          <label for="member-select"><strong>Member auswählen:</strong></label>
          <Dropdown
            id="member-select"
            v-model="newMember.member_id"
            :options="availableMembers"
            optionLabel="name"
            optionValue="member_id"
            placeholder="Member auswählen..."
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label><strong>Allocation: {{ Math.round(newMember.allocation * 100) }}%</strong></label>
          <Slider
            v-model="newMember.allocation"
            :min="0.1"
            :max="1.0"
            :step="0.1"
            class="allocation-slider"
          />
        </div>

        <div class="form-field">
          <label><strong>Assignment von (optional):</strong></label>
          <Calendar
            v-model="newMember.assignment_from_date"
            dateFormat="dd.mm.yy"
            :minDate="sprintStartDate"
            :maxDate="sprintEndDate"
            placeholder="Gesamter Sprint"
            showButtonBar
          />
        </div>

        <div class="form-field">
          <label><strong>Assignment bis (optional):</strong></label>
          <Calendar
            v-model="newMember.assignment_to_date"
            dateFormat="dd.mm.yy"
            :minDate="sprintStartDate"
            :maxDate="sprintEndDate"
            placeholder="Gesamter Sprint"
            showButtonBar
          />
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Abbrechen"
            icon="pi pi-times"
            @click="cancelAddMember"
            class="p-button-secondary p-button-outlined"
          />
          <Button
            label="Hinzufügen"
            icon="pi pi-check"
            @click="addMemberToRoster"
            :disabled="!newMember.member_id"
            class="p-button-success"
          />
        </div>
      </template>
    </Dialog>

    <!-- Confirm Dialog -->
    <Dialog
      v-model:visible="showConfirmDialog"
      modal
      header="Member entfernen"
      :style="{ width: '400px' }"
    >
      <div class="confirm-content">
        <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: #f56565; margin-right: 1rem;"></i>
        <span>
          Möchten Sie "{{ memberToRemove?.member_name || 'Member' }}" wirklich aus dem Sprint-Team entfernen?
        </span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Abbrechen"
            icon="pi pi-times"
            @click="handleCancelRemove"
            class="p-button-secondary p-button-outlined"
          />
          <Button
            label="Entfernen"
            icon="pi pi-check"
            @click="handleConfirmRemove"
            class="p-button-danger"
          />
        </div>
      </template>
    </Dialog>

    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dropdown from 'primevue/dropdown'
import Slider from 'primevue/slider'
import Calendar from 'primevue/calendar'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'
import type { Sprint, SprintRoster, Member } from '@/types/index'

// Props and emits
interface Props {
  visible: boolean
  sprint: Sprint | null
  roster: SprintRoster[]
  members: Member[]
  loading: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'add-member': [data: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }]
  'update-member': [data: { member_id: number; allocation: number; assignment_from?: string; assignment_to?: string }]
  'remove-member': [member_id: number]
}>()

// Services
// const confirm = useConfirm() // Removed to avoid double dialog issue

// Local state
const showAddMember = ref(false)
const showConfirmDialog = ref(false)
const memberToRemove = ref<EnhancedMember | null>(null)
const newMember = ref({
  member_id: null as number | null,
  allocation: 1,
  assignment_from_date: null as Date | null,
  assignment_to_date: null as Date | null
})

// Computed properties
const availableMembers = computed(() => {
  const rosterMemberIds = new Set(props.roster.map(r => r.member_id))
  return props.members.filter(m => !rosterMemberIds.has(m.member_id) && m.active)
})

const sprintStartDate = computed(() => {
  return props.sprint ? new Date(props.sprint.start_date) : new Date()
})

const sprintEndDate = computed(() => {
  return props.sprint ? new Date(props.sprint.end_date) : new Date()
})

// Helper functions
const formatDateForApi = (date: Date | null): string | undefined => {
  if (!date) return undefined
  return date.toISOString().split('T')[0]
}

const parseDateFromApi = (dateString: string | null | undefined): Date | null => {
  if (!dateString) return null
  return new Date(dateString)
}

// Enhanced roster with date objects for Calendar components
const roster = computed(() => {
  return props.roster.map(member => ({
    ...member,
    allocation: Number.parseFloat(member.allocation.toString()),
    assignment_from_date: parseDateFromApi(member.assignment_from),
    assignment_to_date: parseDateFromApi(member.assignment_to)
  }))
})

// Enhanced member type with date objects
type EnhancedMember = SprintRoster & {
  allocation: number
  assignment_from_date: Date | null
  assignment_to_date: Date | null
  member_name?: string
}

// Actions
const updateMember = (member: EnhancedMember) => {
  emit('update-member', {
    member_id: member.member_id,
    allocation: member.allocation,
    assignment_from: formatDateForApi(member.assignment_from_date),
    assignment_to: formatDateForApi(member.assignment_to_date)
  })
}

const addMemberToRoster = () => {
  if (!newMember.value.member_id) return

  emit('add-member', {
    member_id: newMember.value.member_id,
    allocation: newMember.value.allocation,
    assignment_from: formatDateForApi(newMember.value.assignment_from_date),
    assignment_to: formatDateForApi(newMember.value.assignment_to_date)
  })

  cancelAddMember()
}

const cancelAddMember = () => {
  showAddMember.value = false
  newMember.value = {
    member_id: null,
    allocation: 1,
    assignment_from_date: null,
    assignment_to_date: null
  }
}

const confirmRemoveMember = (member: EnhancedMember) => {
  memberToRemove.value = member
  showConfirmDialog.value = true
}

const handleConfirmRemove = () => {
  if (memberToRemove.value) {
    emit('remove-member', memberToRemove.value.member_id)
    showConfirmDialog.value = false
    memberToRemove.value = null
  }
}

const handleCancelRemove = () => {
  showConfirmDialog.value = false
  memberToRemove.value = null
}

// Watch for dialog close
watch(() => props.visible, (newValue) => {
  if (!newValue) {
    showAddMember.value = false
    showConfirmDialog.value = false
    memberToRemove.value = null
    cancelAddMember()
  }
})
</script>

<style scoped>
.roster-content {
  min-height: 400px;
}

.loading-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #7f8c8d;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
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

.team-members {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.member-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.member-info {
  padding: 0;
}

.member-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.member-header h4 {
  margin: 0;
  color: #2c3e50;
}

.member-details {
  display: grid;
  gap: 1.5rem;
}

.allocation-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.allocation-slider {
  width: 100%;
}

.assignment-dates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.date-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.date-field label {
  font-size: 0.9rem;
  color: #495057;
}

.add-member-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-size: 0.9rem;
  color: #495057;
}

.allocation-label,
.field-label {
  font-size: 0.9rem;
  color: #495057;
  margin-bottom: 0.5rem;
}

.dialog-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.w-full {
  width: 100%;
}

.confirm-content {
  display: flex;
  align-items: center;
  padding: 1rem 0;
}

@media (max-width: 768px) {
  .assignment-dates {
    grid-template-columns: 1fr;
  }
}
</style>
