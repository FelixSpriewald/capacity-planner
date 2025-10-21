import { vi } from 'vitest'
import type { DayAvailability, MemberAvailability, Sprint } from '@/types'

export const mockSprint: Sprint = {
  sprint_id: 1,
  name: 'Sprint W43',
  start_date: '2025-10-20',
  end_date: '2025-10-26',
  status: 'active'
}

export const mockMembers = [
  {
    member_id: 1,
    name: 'Alice Developer',
    employment_ratio: 1,
    region_code: 'DE-NW',
    active: true
  },
  {
    member_id: 2,
    name: 'Bob Tester',
    employment_ratio: 0.8,
    region_code: 'UA',
    active: true
  }
]

export const mockDayAvailability: DayAvailability = {
  day: '2025-10-20',
  auto_status: 'available',
  override_state: null,
  final_state: 'available'
}

export const mockDayWithOverride: DayAvailability = {
  day: '2025-10-21',
  auto_status: 'available',
  override_state: 'half',
  final_state: 'half',
  reason: 'Partial availability'
}

export const mockWeekendDay: DayAvailability = {
  day: '2025-10-25',
  auto_status: 'weekend',
  override_state: null,
  final_state: 'weekend'
}

export const mockHolidayDay: DayAvailability = {
  day: '2025-10-24',
  auto_status: 'holiday',
  override_state: null,
  final_state: 'holiday'
}

export const mockMemberAvailability: MemberAvailability = {
  member_id: 1,
  member_name: 'Alice Developer',
  allocation: 1.0,
  days: [
    mockDayAvailability,
    mockDayWithOverride,
    {
      day: '2025-10-22',
      auto_status: 'available',
      override_state: null,
      final_state: 'available'
    },
    {
      day: '2025-10-23',
      auto_status: 'available',
      override_state: 'out',
      final_state: 'out'
    },
    mockHolidayDay,
    mockWeekendDay,
    {
      day: '2025-10-26',
      auto_status: 'weekend',
      override_state: null,
      final_state: 'weekend'
    }
  ],
  summary: {
    total_days: 2.5, // 1 + 0.5 + 1 + 0 (out) = 2.5
    total_hours: 20 // 2.5 * 8 hours
  }
}

export const mockAvailabilityResponse = {
  sprint_id: 1,
  members: [
    {
      member_id: 1,
      member_name: 'Alice Developer',
      days: [
        { day: '2025-10-20', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-21', auto_status: 'available', override_state: 'half', final_state: 'half', reason: 'Dentist appointment' },
        { day: '2025-10-22', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-23', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-24', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-25', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' },
        { day: '2025-10-26', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' }
      ],
      summary: {
        total_hours: 32,
        total_days: 4.5
      }
    },
    {
      member_id: 2,
      member_name: 'Bob Tester',
      days: [
        { day: '2025-10-20', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-21', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-22', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-23', auto_status: 'holiday', override_state: null, final_state: 'holiday', reason: 'National Holiday' },
        { day: '2025-10-24', auto_status: 'available', override_state: null, final_state: 'available', reason: null },
        { day: '2025-10-25', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' },
        { day: '2025-10-26', auto_status: 'weekend', override_state: null, final_state: 'weekend', reason: 'Weekend' }
      ],
      summary: {
        total_hours: 25.6,
        total_days: 3.2
      }
    }
  ],
  team_summary: {
    total_hours: 57.6,
    total_days: 7.7
  }
}

// Mock API responses
export const mockApiClient = {
  getAvailability: vi.fn().mockResolvedValue(mockAvailabilityResponse),
  updateAvailabilityOverride: vi.fn().mockResolvedValue({ success: true }),
  updateBulkAvailabilityOverrides: vi.fn().mockResolvedValue({ success: true })
}
