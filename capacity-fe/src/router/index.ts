import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SprintsView from '../views/SprintsView.vue'
import MembersView from '../views/MembersView.vue'
import MemberDetailView from '../views/MemberDetailView.vue'
import DemoView from '../views/DemoView.vue'

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
    {
      path: '/members/:id',
      name: 'member-detail',
      component: MemberDetailView,
      props: true,
    },
    {
      path: '/demo',
      name: 'demo',
      component: DemoView,
    },
  ],
})

export default router
