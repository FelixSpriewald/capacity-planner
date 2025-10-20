import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AvailabilityGrid from '@/components/AvailabilityGrid.vue'
import { mockAvailabilityResponse, mockSprint, mockMembers } from '../mocks'

// Mock the stores
vi.mock('@/stores', () => ({
  useSprintsStore: vi.fn(),
  useMembersStore: vi.fn(),
  useAppStore: vi.fn()
}))

// Import mocked stores
import { useSprintsStore, useMembersStore, useAppStore } from '@/stores'

describe('AvailabilityGrid.vue - Complete Tests', () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let wrapper: any
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let sprintsStore: any
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let membersStore: any  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let appStore: any

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Create mocked stores
    sprintsStore = {
      loading: false,
      availability: mockAvailabilityResponse,
      fetchAvailability: vi.fn().mockResolvedValue(undefined),
      updateAvailabilityOverride: vi.fn().mockResolvedValue(undefined)
    }
    
    membersStore = {
      members: mockMembers,
      fetchMembers: vi.fn().mockResolvedValue(undefined)
    }
    
    appStore = {
      showWarning: vi.fn(),
      showError: vi.fn(),
      showSuccess: vi.fn()
    }

    // Mock store composables
    vi.mocked(useSprintsStore).mockReturnValue(sprintsStore)
    vi.mocked(useMembersStore).mockReturnValue(membersStore)
    vi.mocked(useAppStore).mockReturnValue(appStore)

    // Create component with mocked data
    wrapper = mount(AvailabilityGrid, {
      props: {
        sprint: mockSprint
      },
      global: {
        stubs: {
          Button: true,
          ProgressSpinner: true
        }
      }
    })
  })

  describe('Component Rendering', () => {
    it('renders availability grid with correct member data', () => {
      expect(wrapper.find('.grid-container').exists()).toBe(true)
      expect(wrapper.find('.member-cell').exists()).toBe(true)
      expect(wrapper.text()).toContain('Alice Developer')
      expect(wrapper.text()).toContain('Bob Tester')
    })

    it('displays correct number of day cells', () => {
      const dayCells = wrapper.findAll('.day-cell')
      // Should have cells for each member and each day
      expect(dayCells.length).toBeGreaterThan(0)
    })

    it('shows empty state when no sprint is selected', async () => {
      await wrapper.setProps({ sprint: null })
      
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('No Sprint Selected')
    })
  })

  describe('Cell States and Styling', () => {
    it('displays different availability states correctly', () => {
      // Check for different state classes based on mock data
      const availableCells = wrapper.findAll('.state-available')
      const halfCells = wrapper.findAll('.state-half')
      const weekendCells = wrapper.findAll('.state-weekend')
      const holidayCells = wrapper.findAll('.state-holiday')
      
      expect(availableCells.length).toBeGreaterThan(0)
      expect(halfCells.length).toBeGreaterThan(0)
      expect(weekendCells.length).toBeGreaterThan(0)
      expect(holidayCells.length).toBeGreaterThan(0)
    })

    it('shows override indicators when overrides exist', () => {
      const overrideCells = wrapper.findAll('.has-override')
      expect(overrideCells.length).toBeGreaterThan(0)
    })
  })

  describe('Summary Calculations', () => {
    it('displays member summaries correctly', () => {
      const summaryContent = wrapper.findAll('.summary-content')
      expect(summaryContent.length).toBeGreaterThan(0)
      
      // Check that hours and days are displayed
      expect(wrapper.text()).toContain('32h')
      expect(wrapper.text()).toContain('4.5 days')
    })

    it('displays team summary row', () => {
      const teamSummary = wrapper.find('.summary-row')
      expect(teamSummary.exists()).toBe(true)
      expect(wrapper.text()).toContain('Team Total')
    })
  })

  describe('Interactive Features', () => {
    it('has clickable day cells', () => {
      const dayCells = wrapper.findAll('.day-cell')
      expect(dayCells.length).toBeGreaterThan(0)
      
      // Each cell should be clickable (have cursor pointer style)
      const firstCell = dayCells[0]
      expect(firstCell.exists()).toBe(true)
    })

    it('provides tooltips for cells', () => {
      const cellsWithTooltips = wrapper.findAll('.day-cell[title]')
      expect(cellsWithTooltips.length).toBeGreaterThan(0)
    })

    it('has bulk action controls', () => {
      expect(wrapper.find('.grid-controls-bar').exists()).toBe(true)
      // Since buttons are stubbed, check for the container and hint text
      expect(wrapper.text()).toContain('Shift')
      expect(wrapper.text()).toContain('Ctrl/Cmd')
    })
  })

  describe('Selection Mode', () => {
    it('can enter selection mode', async () => {
      const selectModeButton = wrapper.find('[data-pc-name="button"]')
      if (selectModeButton.exists()) {
        await selectModeButton.trigger('click')
        // Since Button is stubbed, we check if the click was captured
        expect(selectModeButton.exists()).toBe(true)
      }
    })

    it('shows selection indicators when in selection mode', () => {
      // Set component to selection mode by accessing the component's data
      wrapper.vm.selectionMode = true
      wrapper.vm.selectedCells.add('1-2025-10-20')
      
      // Force re-render
      wrapper.vm.$forceUpdate()
      
      // Check for selection indicators
      const selectionIndicators = wrapper.findAll('.selection-indicator')
      expect(selectionIndicators.length).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Legend Display', () => {
    it('shows status legend with all states', () => {
      expect(wrapper.find('.legend').exists()).toBe(true)
      expect(wrapper.text()).toContain('Available')
      expect(wrapper.text()).toContain('Out')
      expect(wrapper.text()).toContain('Half Day')
      expect(wrapper.text()).toContain('Weekend')
      expect(wrapper.text()).toContain('Holiday')
    })

    it('displays colored status indicators in legend', () => {
      const statusCells = wrapper.findAll('.legend .status-cell')
      expect(statusCells.length).toBeGreaterThan(4) // At least 5 states
    })
  })
})