<template>
  <div class="legend-inline">
    <div class="legend-items-compact">
      <div class="legend-item-compact">
        <div class="status-indicator available"></div>
        <span>Verfügbar</span>
      </div>
      <div class="legend-item-compact">
        <div class="status-indicator half"></div>
        <span>Halbtags</span>
      </div>
      <div class="legend-item-compact">
        <div class="status-indicator unavailable"></div>
        <span>Nicht verfügbar</span>
      </div>
      <div class="legend-item-compact">
        <div class="status-indicator holiday"></div>
        <span>Feiertag</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.legend-inline {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.legend-items-compact {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.legend-item-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #4b5563;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(5px);
  transition: all 0.2s ease;
}

.legend-item-compact:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-item-compact .status-indicator.unavailable {
  background: linear-gradient(135deg, #ef4444, #dc2626) !important;
}

.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1);
  flex-shrink: 0;
  transition: all 0.2s ease;
  position: relative;
}

.status-indicator.available {
  background: linear-gradient(135deg, #10b981, #059669);
}
.status-indicator.half {
  background: linear-gradient(90deg, #f59e0b 50%, #fbbf24 50%);
}
.status-indicator.unavailable {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}
.status-indicator.holiday {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}
.status-indicator.unknown {
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
  opacity: 0.7;
}
</style>