import { config } from '@vue/test-utils'

// Global test setup
config.global.mocks = {
  // Mock global properties if needed
}

// Mock PrimeVue components globally if needed
config.global.stubs = {
  'router-link': true,
  'router-view': true
}
