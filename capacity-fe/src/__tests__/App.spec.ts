import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import PrimeVue from 'primevue/config'
import Button from 'primevue/button'
import TooltipDirective from 'primevue/tooltip'
import App from '../App.vue'
import HomeView from '../views/HomeView.vue'

describe('App', () => {
  it('mounts renders properly', () => {
    const pinia = createPinia()
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: HomeView }
      ]
    })

    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router, PrimeVue],
        components: {
          Button
        },
        directives: {
          tooltip: TooltipDirective
        }
      }
    })

    expect(wrapper.find('nav').exists()).toBe(true)
  })
})
