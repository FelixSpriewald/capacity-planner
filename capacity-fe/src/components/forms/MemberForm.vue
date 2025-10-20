<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    :header="isEdit ? 'Member bearbeiten' : 'Neues Member hinzufügen'"
    :style="{ width: '500px' }"
    @hide="resetForm"
  >
    <form @submit.prevent="handleSubmit" class="member-form">
      <div class="form-field">
        <label for="name" class="form-label">Name *</label>
        <InputText
          id="name"
          v-model="form.name"
          placeholder="z.B. Alice Schmidt"
          :class="{ 'p-invalid': errors.name }"
          class="w-full"
        />
        <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
      </div>

      <div class="form-field">
        <label for="employment_ratio" class="form-label">Arbeitszeit *</label>
        <div class="input-with-suffix">
          <InputNumber
            id="employment_ratio"
            v-model="form.employment_ratio"
            :min="0.1"
            :max="1"
            :step="0.1"
            :min-fraction-digits="1"
            :max-fraction-digits="2"
            :class="{ 'p-invalid': errors.employment_ratio }"
            class="w-full"
            placeholder="1.0"
          />
          <span class="input-suffix">{{ employmentPercentage }}%</span>
        </div>
        <small v-if="errors.employment_ratio" class="p-error">{{ errors.employment_ratio }}</small>
        <small class="form-help">Vollzeit = 1.0, Teilzeit = 0.5, etc.</small>
      </div>

      <div class="form-field">
        <label for="region_code" class="form-label">Region *</label>
        <Dropdown
          id="region_code"
          v-model="form.region_code"
          :options="regionOptions"
          option-label="label"
          option-value="value"
          placeholder="Region auswählen"
          :class="{ 'p-invalid': errors.region_code }"
          class="w-full"
        />
        <small v-if="errors.region_code" class="p-error">{{ errors.region_code }}</small>
        <small class="form-help">Bestimmt Feiertage und Zeitzonen</small>
      </div>



      <div class="form-actions">
        <Button
          type="button"
          label="Abbrechen"
          severity="secondary"
          @click="$emit('update:visible', false)"
          class="flex-1"
        />
        <Button
          type="submit"
          :label="isEdit ? 'Speichern' : 'Hinzufügen'"
          :loading="loading"
          class="flex-1"
        />
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import type { Member } from '@/types'

interface MemberForm {
  name: string
  employment_ratio: number
  region_code: string
}

interface Props {
  visible: boolean
  member?: Member | null
  loading?: boolean
}

interface Emits {
  (e: 'hide'): void
  (e: 'submit', data: MemberForm): void
  (e: 'update:visible', visible: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  member: null,
  loading: false
})

const emit = defineEmits<Emits>()

const form = ref<MemberForm>({
  name: '',
  employment_ratio: 1,
  region_code: ''
})

const errors = ref<Partial<Record<keyof MemberForm, string>>>({})

const regionOptions = [
  { label: 'Deutschland - Nordrhein-Westfalen', value: 'DE-NW' },
  { label: 'Deutschland - Bayern', value: 'DE-BY' },
  { label: 'Deutschland - Baden-Württemberg', value: 'DE-BW' },
  { label: 'Deutschland - Hessen', value: 'DE-HE' },
  { label: 'Deutschland - Berlin', value: 'DE-BE' },
  { label: 'Österreich', value: 'AT' },
  { label: 'Schweiz', value: 'CH' },
  { label: 'Ukraine', value: 'UA' },
  { label: 'Polen', value: 'PL' },
  { label: 'Tschechien', value: 'CZ' }
]

const isEdit = computed(() => !!props.member)

const employmentPercentage = computed(() =>
  Math.round((form.value.employment_ratio || 0) * 100)
)

function validateForm(): boolean {
  errors.value = {}
  let isValid = true

  if (!form.value.name.trim()) {
    errors.value.name = 'Name ist erforderlich'
    isValid = false
  } else if (form.value.name.trim().length < 2) {
    errors.value.name = 'Name muss mindestens 2 Zeichen lang sein'
    isValid = false
  }

  if (!form.value.employment_ratio || form.value.employment_ratio <= 0) {
    errors.value.employment_ratio = 'Arbeitszeit muss größer als 0 sein'
    isValid = false
  } else if (form.value.employment_ratio > 1) {
    errors.value.employment_ratio = 'Arbeitszeit kann nicht über 100% liegen'
    isValid = false
  }

  if (!form.value.region_code) {
    errors.value.region_code = 'Region ist erforderlich'
    isValid = false
  }

  return isValid
}

function handleSubmit() {
  if (validateForm()) {
    emit('submit', { ...form.value })
  }
}

function resetForm() {
  form.value = {
    name: '',
    employment_ratio: 1,
    region_code: ''
  }
  errors.value = {}
}

function loadMemberData() {
  if (props.member) {
    form.value = {
      name: props.member.name,
      employment_ratio: props.member.employment_ratio,
      region_code: props.member.region_code
    }
  } else {
    resetForm()
  }
}

watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    nextTick(() => {
      loadMemberData()
    })
  }
})

watch(() => props.member, () => {
  if (props.visible) {
    loadMemberData()
  }
})
</script>

<style scoped>
.member-form {
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
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.input-with-suffix {
  position: relative;
  display: flex;
  align-items: center;
}

.input-suffix {
  position: absolute;
  right: 12px;
  color: #6c757d;
  font-size: 0.9rem;
  pointer-events: none;
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-label {
  font-weight: 500;
  color: #2c3e50;
  cursor: pointer;
}

.form-help {
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.flex-1 {
  flex: 1;
}

.p-error {
  color: #e74c3c;
  font-size: 0.8rem;
}

.p-invalid {
  border-color: #e74c3c;
}

.w-full {
  width: 100%;
}
</style>
