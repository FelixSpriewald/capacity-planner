import type { Member, Sprint, AvailabilityResponse, SprintRoster } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private readonly baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Health Check
  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health')
  }

  // Members API
  async getMembers(includeInactive: boolean = false): Promise<Member[]> {
    const params = includeInactive ? '?include_inactive=true' : ''
    return this.request<Member[]>(`/api/v1/members/${params}`)
  }

  async getMember(id: number): Promise<Member> {
    return this.request<Member>(`/api/v1/members/${id}`)
  }

  async createMember(member: Omit<Member, 'member_id'>): Promise<Member> {
    return this.request<Member>('/api/v1/members/', {
      method: 'POST',
      body: JSON.stringify(member),
    })
  }

  async updateMember(id: number, member: Omit<Member, 'member_id'>): Promise<Member> {
    return this.request<Member>(`/api/v1/members/${id}`, {
      method: 'PUT',
      body: JSON.stringify(member),
    })
  }

  async deleteMember(id: number): Promise<void> {
    return this.request<void>(`/api/v1/members/${id}`, {
      method: 'DELETE',
    })
  }

  // Sprints API
  async getSprints(): Promise<Sprint[]> {
    return this.request<Sprint[]>('/api/v1/sprints/')
  }

  async getSprint(id: number): Promise<Sprint> {
    return this.request<Sprint>(`/api/v1/sprints/${id}`)
  }

  async createSprint(sprint: Omit<Sprint, 'sprint_id'>): Promise<Sprint> {
    return this.request<Sprint>('/api/v1/sprints/', {
      method: 'POST',
      body: JSON.stringify(sprint),
    })
  }

  async updateSprint(id: number, sprint: Partial<Sprint>): Promise<Sprint> {
    return this.request<Sprint>(`/api/v1/sprints/${id}`, {
      method: 'PUT',
      body: JSON.stringify(sprint),
    })
  }

  async deleteSprint(id: number): Promise<void> {
    return this.request<void>(`/api/v1/sprints/${id}`, {
      method: 'DELETE',
    })
  }

  // Availability API
  async getSprintAvailability(sprintId: number): Promise<AvailabilityResponse> {
    return this.request<AvailabilityResponse>(`/api/v1/sprints/${sprintId}/availability`)
  }

  async updateAvailabilityOverride(
    sprintId: number,
    memberId: number,
    day: string,
    data: { state: 'available' | 'out' | 'half' | null; reason?: string },
  ): Promise<void> {
    return this.request<void>(`/api/v1/sprints/${sprintId}/availability/${memberId}/${day}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  // Sprint Roster API
  async getSprintRoster(sprintId: number): Promise<SprintRoster[]> {
    return this.request<SprintRoster[]>(`/api/v1/sprints/${sprintId}/roster`)
  }

  async updateSprintRoster(
    sprintId: number,
    memberId: number,
    data: { allocation: number; assignment_from?: string; assignment_to?: string },
  ): Promise<void> {
    return this.request<void>(`/api/v1/sprints/${sprintId}/roster/${memberId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient
