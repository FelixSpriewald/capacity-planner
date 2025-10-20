// Demo data for Task 12: Alice(DE-NW), Bogdan(UA), Sprint W43
import type { Sprint, Member, AvailabilityResponse } from '@/types'

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

export const demoSprint: Sprint = {
  sprint_id: 1,
  name: 'Sprint W43',
  start_date: '2025-10-20',
  end_date: '2025-10-31',
  status: 'active'
}

export const demoAvailabilityResponse: AvailabilityResponse = {
  sprint: demoSprint,
  members: [
    {
      member_id: 1,
      member_name: 'Alice Developer',
      days: [
        // Week 1
        { day: '2025-10-20', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-21', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-22', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-23', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-24', auto_status: 'pto', override_state: null, final_state: 'pto', reason: 'PTO: Long weekend' },
        { day: '2025-10-25', auto_status: 'weekend', override_state: null, final_state: 'weekend' },
        { day: '2025-10-26', auto_status: 'weekend', override_state: null, final_state: 'weekend' },
        // Week 2
        { day: '2025-10-27', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-28', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-29', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-30', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-31', auto_status: 'holiday', override_state: null, final_state: 'holiday', reason: 'Reformationstag (DE-NW)' }
      ],
      summary: {
        total_hours: 56, // 7 available days * 8 hours
        total_days: 7
      }
    },
    {
      member_id: 2,
      member_name: 'Bogdan Coder',
      days: [
        // Week 1
        { day: '2025-10-20', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-21', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-22', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-23', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-24', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-25', auto_status: 'weekend', override_state: null, final_state: 'weekend' },
        { day: '2025-10-26', auto_status: 'weekend', override_state: null, final_state: 'weekend' },
        // Week 2
        { day: '2025-10-27', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-28', auto_status: 'holiday', override_state: null, final_state: 'holiday', reason: 'День транспорту (UA)' },
        { day: '2025-10-29', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-30', auto_status: 'available', override_state: null, final_state: 'available' },
        { day: '2025-10-31', auto_status: 'available', override_state: null, final_state: 'available' } // No Reformationstag for UA
      ],
      summary: {
        total_hours: 64, // 8 available days * 8 hours
        total_days: 8
      }
    }
  ],
  team_summary: {
    total_hours: 120,
    total_days: 15
  }
}

export default {
  demoMembers,
  demoSprint,
  demoAvailabilityResponse
}
