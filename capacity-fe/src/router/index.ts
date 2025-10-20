import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SprintsView from '../views/SprintsView.vue'
import MembersView from '../views/MembersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sprints',
      name: 'sprints',
      component: SprintsView,
    },
    {
      path: '/members',
      name: 'members',
      component: MembersView,
    },
  ],
})

export default router
