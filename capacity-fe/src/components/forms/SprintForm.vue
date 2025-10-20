<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    :header="isEdit ? 'Sprint bearbeiten' : 'Neuen Sprint erstellen'"
    :style="{ width: '600px' }"
    @hide="resetForm"
  >
    <form @submit.prevent="handleSubmit" class="sprint-form">
      <div class="form-field">
        <label for="name" class="form-label">Sprint Name *</label>
        <InputText
          id="name"
          v-model="form.name"
          placeholder="z.B. Sprint W43-44 2025"
          :class="{ 'p-invalid': errors.name }"
          class="w-full"
        />
        <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
      </div>

      <div class="form-grid">
        <div class="form-field">
          <label for="start_date" class="form-label">Start Datum *</label>
          <Calendar
            id="start_date"
            v-model="form.start_date"
            dateFormat="dd.mm.yy"
            showIcon
            :class="{ 'p-invalid': errors.start_date }"
            class="w-full"
            placeholder="Start Datum wählen"
          />
          <small v-if="errors.start_date" class="p-error">{{ errors.start_date }}</small>
        </div>

        <div class="form-field">
          <label for="end_date" class="form-label">End Datum *</label>
          <Calendar
            id="end_date"
            v-model="form.end_date"
            dateFormat="dd.mm.yy"
            showIcon
            :class="{ 'p-invalid': errors.end_date }"
            class="w-full"
            placeholder="End Datum wählen"
          />
          <small v-if="errors.end_date" class="p-error">{{ errors.end_date }}</small>
        </div>
      </div>

      <div class="form-field" v-if="isEdit">
        <label for="status" class="form-label">Status</label>
        <Dropdown
          id="status"
          v-model="form.status"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Status wählen"
          class="w-full"
        />
      </div>

      <div class="sprint-info" v-if="form.start_date && form.end_date">
        <div class="info-card">
          <h4>Sprint Informationen</h4>
          <div class="info-row">
            <span>Dauer:</span>
            <strong>{{ sprintDuration }} Tage</strong>
          </div>
          <div class="info-row">
            <span>Arbeitstage:</span>
            <strong>{{ workingDays }} Tage</strong>
          </div>
          <div class="info-row">
            <span>Wochenenden:</span>
            <strong>{{ weekendDays }} Tage</strong>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <Button
          label="Abbrechen"
          severity="secondary"
          @click="$emit('update:visible', false)"
          type="button"
        />
        <Button
          :label="isEdit ? 'Aktualisieren' : 'Erstellen'"
          type="submit"
          :loading="loading"
          :disabled="!isFormValid"
        />
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import type { Sprint, SprintStatus } from '@/types'

interface Props {
  visible: boolean
  sprint?: Sprint | null
  loading?: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: { name: string; start_date: string; end_date: string; status?: SprintStatus }): void
}

const props = withDefaults(defineProps<Props>(), {
  sprint: null,
  loading: false
})

const emit = defineEmits<Emits>()

// Form state
const form = ref({
  name: '',
  start_date: null as Date | null,
  end_date: null as Date | null,
  status: 'draft' as SprintStatus
})

const errors = ref({
  name: '',
  start_date: '',
  end_date: ''
})

// Status options
const statusOptions = [
  { label: 'Entwurf', value: 'draft' },
  { label: 'Aktiv', value: 'active' },
  { label: 'Abgeschlossen', value: 'completed' }
]

// Computed
const isEdit = computed(() => !!props.sprint)

const isFormValid = computed(() => {
  // Basic validation - just check if required fields have values
  const hasName = form.value.name.trim() !== ''
  const hasStartDate = form.value.start_date !== null
  const hasEndDate = form.value.end_date !== null
  
  return hasName && hasStartDate && hasEndDate
})

const sprintDuration = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  const diffTime = Math.abs(form.value.end_date.getTime() - form.value.start_date.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
})

const workingDays = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  
  let count = 0
  const start = new Date(form.value.start_date)
  const end = new Date(form.value.end_date)
  
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const day = d.getDay()
    if (day !== 0 && day !== 6) { // Monday = 1, Sunday = 0
      count++
    }
  }
  
  return count
})

const weekendDays = computed(() => {
  return sprintDuration.value - workingDays.value
})

// Watchers
watch(() => props.visible, (visible) => {
  if (visible) {
    resetForm()
    if (props.sprint) {
      loadSprintData()
    }
  }
})

// Methods
const resetForm = () => {
  form.value = {
    name: '',
    start_date: null,
    end_date: null,
    status: 'draft'
  }
  
  errors.value = {
    name: '',
    start_date: '',
    end_date: ''
  }
}

const loadSprintData = () => {
  if (!props.sprint) return
  
  form.value = {
    name: props.sprint.name,
    start_date: new Date(props.sprint.start_date),
    end_date: new Date(props.sprint.end_date),
    status: props.sprint.status
  }
}

const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0] || ''
}

const handleSubmit = () => {
  // Clear previous errors
  errors.value = {
    name: '',
    start_date: '',
    end_date: ''
  }
  
  // Validate on submit
  if (!form.value.name.trim()) {
    errors.value.name = 'Sprint Name ist erforderlich'
  } else if (form.value.name.length < 3) {
    errors.value.name = 'Sprint Name muss mindestens 3 Zeichen lang sein'
  }
  
  if (!form.value.start_date) {
    errors.value.start_date = 'Start Datum ist erforderlich'
  }
  
  if (!form.value.end_date) {
    errors.value.end_date = 'End Datum ist erforderlich'
  } else if (form.value.start_date && form.value.end_date <= form.value.start_date) {
    errors.value.end_date = 'End Datum muss nach dem Start Datum liegen'
  }
  
  // Check if there are any errors
  const hasErrors = errors.value.name || errors.value.start_date || errors.value.end_date
  if (hasErrors) {
    return
  }
  
  const formData = {
    name: form.value.name.trim(),
    start_date: formatDate(form.value.start_date!),
    end_date: formatDate(form.value.end_date!),
    ...(isEdit.value && { status: form.value.status })
  }
  
  emit('submit', formData)
}
</script>

<style scoped>
.sprint-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: #374151;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.sprint-info {
  margin: 1rem 0;
}

.info-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
}

.info-card h4 {
  margin: 0 0 0.75rem 0;
  color: #495057;
  font-size: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px solid #dee2e6;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

.p-error {
  color: #dc3545;
  font-size: 0.875rem;
}

.p-invalid {
  border-color: #dc3545;
}
</style>