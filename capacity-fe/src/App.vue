<script setup lang="ts">
import Navigation from '@/components/Navigation.vue'
import Toast from 'primevue/toast'
</script>

<template>
  <div id="app">
    <Navigation />
    <main class="main-content">
      <RouterView />
    </main>
    <Toast />
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.main-content {
  padding: 1rem;
}
</style>
