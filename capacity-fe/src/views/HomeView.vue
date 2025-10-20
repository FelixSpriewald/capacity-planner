<template>
  <div class="home-view">
    <div class="hero-section">
      <h1 class="title">
        <i class="pi pi-calendar-clock"></i>
        Capacity Planner
      </h1>
      <p class="subtitle">Sprint-basierte Kapazitätsplanung für dein Team</p>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <i class="pi pi-users feature-icon"></i>
        <h3>Team Management</h3>
        <p>Verwalte Teammitglieder mit Arbeitszeit und Region</p>
        <Button
          label="Zu Members"
          icon="pi pi-arrow-right"
          @click="$router.push('/members')"
          class="p-button-sm"
        />
      </div>

      <div class="feature-card">
        <i class="pi pi-calendar feature-icon"></i>
        <h3>Sprint Planning</h3>
        <p>Erstelle Sprints und plane Kapazitäten mit Availability Grid</p>
        <Button
          label="Zu Sprints"
          icon="pi pi-arrow-right"
          @click="$router.push('/sprints')"
          class="p-button-sm"
        />
      </div>

      <div class="feature-card">
        <i class="pi pi-chart-line feature-icon"></i>
        <h3>Availability Matrix</h3>
        <p>Übersicht über PTO, Feiertage und Overrides</p>
        <Button
          label="Demo anzeigen"
          icon="pi pi-eye"
          @click="showDemo"
          class="p-button-sm p-button-outlined"
        />
      </div>
    </div>

    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-value">{{ stats.members }}</div>
        <div class="stat-label">Team Members</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.sprints }}</div>
        <div class="stat-label">Active Sprints</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.capacity }}h</div>
        <div class="stat-label">Total Capacity</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'

const stats = ref({
  members: 0,
  sprints: 0,
  capacity: 0,
})

const showDemo = () => {
  // Placeholder für Demo-Funktionalität
  console.log('Demo wird angezeigt...')
}

onMounted(async () => {
  // Placeholder für API-Calls
  // Hier würden wir echte Daten vom Backend laden
  stats.value = {
    members: 2,
    sprints: 1,
    capacity: 320,
  }
})
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
}

.title {
  font-size: 3rem;
  font-weight: 300;
  color: #2c3e50;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.title .pi {
  color: #3498db;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin: 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s ease-in-out;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 3rem;
  color: #3498db;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 3rem;
}

.stat-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
