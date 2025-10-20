<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <nav class="main-nav">
    <div class="nav-brand">
      <router-link to="/" class="brand-link">
        <i class="pi pi-calendar-clock brand-icon"></i>
        <span class="brand-text">Capacity Planner</span>
      </router-link>
    </div>

    <div class="nav-menu">
      <router-link
        v-for="item in navigationItems"
        :key="item.route"
        :to="item.route"
        class="nav-item"
      >
        <i :class="`pi ${item.icon}`"></i>
        <span>{{ item.label }}</span>
        <Badge v-if="item.badge" :value="item.badge" severity="secondary" class="nav-badge" />
      </router-link>
    </div>

    <div class="nav-actions">
      <Button
        icon="pi pi-cog"
        class="p-button-text p-button-sm"
        @click="openSettings"
        v-tooltip="'Einstellungen'"
      />
      <Button
        icon="pi pi-question-circle"
        class="p-button-text p-button-sm"
        @click="openHelp"
        v-tooltip="'Hilfe'"
      />
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import type { NavigationItem } from '@/types'
import { useSprintsStore, useMembersStore } from '@/stores'
const sprintsStore = useSprintsStore()
const membersStore = useMembersStore()

const navigationItems = computed<NavigationItem[]>(() => [
  {
    label: 'Dashboard',
    icon: 'pi-home',
    route: '/',
  },
  {
    label: 'Members',
    icon: 'pi-users',
    route: '/members',
    badge: membersStore.stats.active.toString(),
  },
  {
    label: 'Sprints',
    icon: 'pi-calendar',
    route: '/sprints',
    badge: sprintsStore.stats.active.toString(),
  },
  {
    label: 'Demo',
    icon: 'pi-star',
    route: '/demo',
  },
])

const openSettings = () => {
  console.log('Einstellungen öffnen...')
}

const openHelp = () => {
  console.log('Hilfe öffnen...')
}
</script>

<style scoped>
.main-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.25rem;
  transition: color 0.2s ease-in-out;
}

.brand-link:hover {
  color: #3498db;
}

.brand-icon {
  font-size: 1.5rem;
  color: #3498db;
}

.brand-text {
  font-weight: 300;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #7f8c8d;
  border-radius: 6px;
  transition: all 0.2s ease-in-out;
  position: relative;
  font-weight: 500;
}

.nav-item:hover {
  color: #3498db;
  background: #f8f9fa;
}

.nav-item.router-link-active {
  color: #3498db;
  background: #e3f2fd;
}

.nav-item i {
  font-size: 1rem;
}

.nav-badge {
  margin-left: 0.5rem;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .main-nav {
    padding: 1rem;
  }

  .nav-menu {
    gap: 1rem;
  }

  .nav-item {
    padding: 0.5rem 0.75rem;
  }

  .nav-item span {
    display: none;
  }

  .brand-text {
    display: none;
  }
}

@media (max-width: 480px) {
  .nav-menu {
    gap: 0.5rem;
  }

  .nav-actions {
    gap: 0.25rem;
  }
}
</style>
