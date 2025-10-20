import type { Sprint, Member, AvailabilityResponse } from '@/types'

// Define missing types for demo
interface PTOResponse {
  pto_id: number
  member_id: number
  from_date: string
  to_date: string
  type: string
  notes?: string
}

interface HolidayResponse {
  holiday_id: number
  date: string
  region_code: string
  name: string
  is_company_day: boolean
}

// Demo Members matching Task 12 requirements
export const demoMembers: Member[] = [
  {
    member_id: 1,
    name: 'Alice Developer',
    employment_ratio: 1,
    region_code: 'DE-NW',
    active: true
  },
  {
    member_id: 2,
    name: 'Bogdan Coder',
    employment_ratio: 1,
    region_code: 'UA',
    active: true
  }
]

// Sprint W43 (2 weeks Mo-Fr) - October 2025
export const demoSprint: Sprint = {
  sprint_id: 1,
  name: 'Sprint W43',
  start_date: '2025-10-20',
  end_date: '2025-10-31',
  status: 'active'
}

// Demo PTO: 1 day for Alice
export const demoPTO: PTOResponse[] = [
  {
    pto_id: 1,
    member_id: 1,
    from_date: '2025-10-24',
    to_date: '2025-10-24',
    type: 'vacation',
    notes: 'Long weekend'
  }
]

// Demo Holidays
export const demoHolidays: HolidayResponse[] = [
  // German holiday (Reformationstag) - DE-NW
  {
    holiday_id: 1,
    date: '2025-10-31',
    region_code: 'DE-NW',
    name: 'Reformationstag',
    is_company_day: false
  },
  // Ukrainian holiday (example)
  {
    holiday_id: 2,
    date: '2025-10-28',
    region_code: 'UA',
    name: 'День працівників автомобільного транспорту',
    is_company_day: false
  }
]

// Complete demo availability data for Sprint W43
export const demoAvailabilityResponse: AvailabilityResponse = {
  sprint: demoSprint,
  members: [
    {
      member_id: 1,
      member_name: 'Alice Developer',
      days: [
        // Week 1: October 20-24, 2025
        { day: '2025-10-20', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-21', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-22', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-23', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-24', auto_status: 'pto', override_state: null, final_state: 'pto', reason: 'PTO: Long weekend' },
        { day: '2025-10-25', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' },
        { day: '2025-10-26', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' },

        // Week 2: October 27-31, 2025
        { day: '2025-10-27', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-28', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-29', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-30', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-31', auto_status: 'holiday', override_state: null, final_state: 'holiday', reason: 'Holiday: Reformationstag (DE-NW)' }
      ],
      summary: {
        total_hours: 56, // 7 available days * 8 hours
        total_days: 7.0
      }
    },
    {
      member_id: 2,
      member_name: 'Bogdan Coder',
      days: [
        // Week 1: October 20-24, 2025
        { day: '2025-10-20', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-21', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-22', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-23', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-24', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-25', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' },
        { day: '2025-10-26', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' },

        // Week 2: October 27-31, 2025
        { day: '2025-10-27', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-28', auto_status: 'holiday', override_state: null, final_state: 'holiday', reason: 'Holiday: День працівників автомобільного транспорту (UA)' },
        { day: '2025-10-29', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-30', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-31', auto_status: 'available', override_state: null, final_state: 'available', reason: null } // No Reformationstag for UA
      ],
      summary: {
        total_hours: 64, // 8 available days * 8 hours
        total_days: 8.0
      }
    }
  ],
  team_summary: {
    total_hours: 120, // 56 + 64
    total_days: 15.0  // 7 + 8
  }
}

export default {
  demoMembers,
  demoSprint,
  demoPTO,
  demoHolidays,
  demoAvailabilityResponse
}
