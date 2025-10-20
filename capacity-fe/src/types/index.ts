// API Types
export type SprintStatus = 'planned' | 'active' | 'finished'
export type PTOType = 'vacation' | 'sick' | 'personal'
export type OverrideState = 'available' | 'out' | 'half' | null
export type AutoStatus = 'weekend' | 'holiday' | 'pto' | 'out_of_assignment' | 'available'
export type FinalState =
  | 'weekend'
  | 'holiday'
  | 'pto'
  | 'out_of_assignment'
  | 'available'
  | 'out'
  | 'half'
export type ToastSeverity = 'success' | 'info' | 'warn' | 'error'

export interface Member {
  member_id: number
  name: string
  employment_ratio: number
  region_code: string
  active: boolean
}

export interface Sprint {
  sprint_id: number
  name: string
  start_date: string
  end_date: string
  status: SprintStatus
  // Optional statistics
  member_count?: number
  total_capacity_hours?: number
  working_days?: number
}

export interface SprintRoster {
  sprint_id: number
  member_id: number
  allocation: number
  assignment_from?: string | null
  assignment_to?: string | null
}

export interface Holiday {
  holiday_id: number
  date: string
  region_code: string
  name: string
  is_company_day: boolean
}

export interface PTO {
  pto_id: number
  member_id: number
  from_date: string
  to_date: string
  type: PTOType
  notes?: string
}

export interface AvailabilityOverride {
  sprint_id: number
  member_id: number
  day: string
  state: OverrideState
  reason?: string
}

export interface DayAvailability {
  day: string
  auto_status: AutoStatus
  override_state: OverrideState
  final_state: FinalState
  reason?: string
}

export interface MemberAvailability {
  member_id: number
  member_name: string
  allocation: number
  days: DayAvailability[]
  summary: {
    total_days: number
    total_hours: number
  }
}

export interface AvailabilityResponse {
  sprint: Sprint
  members: MemberAvailability[]
  team_summary: {
    total_days: number
    total_hours: number
  }
}

// UI Types
export interface NavigationItem {
  label: string
  icon: string
  route: string
  badge?: string | number
}

export interface ToastMessage {
  severity: ToastSeverity
  summary: string
  detail?: string
  life?: number
}

// Form Types
export interface MemberFormData {
  name: string
  employment_ratio: number
  region_code: string
  active: boolean
}

export interface SprintFormData {
  name: string
  start_date: string
  end_date: string
}

export interface PTOFormData {
  member_id: number
  from_date: string
  to_date: string
  type: PTOType
  notes?: string
}

// Store Types
export interface AppState {
  loading: boolean
  error: string | null
}

export interface MembersState extends AppState {
  members: Member[]
  selectedMember: Member | null
}

export interface SprintsState extends AppState {
  sprints: Sprint[]
  selectedSprint: Sprint | null
  availability: AvailabilityResponse | null
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface ApiError {
  detail: string
  status_code: number
}

// Filter and Sort Types
export interface MemberFilter {
  active?: boolean
  region_code?: string
  search?: string
}

export interface SprintFilter {
  name?: string
  date_from?: string
  date_to?: string
}

export type SortDirection = 'asc' | 'desc'

export interface SortOption {
  field: string
  direction: SortDirection
}
