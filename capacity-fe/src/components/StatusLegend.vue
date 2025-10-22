<template>
  <div class="legend-inline">
    <div class="legend-items-compact">
      <div class="legend-item-compact available">
        <span>Verfügbar</span>
      </div>
      <div class="legend-item-compact half">
        <span>Halbtags</span>
      </div>
      <div class="legend-item-compact unavailable">
        <span>Nicht verfügbar</span>
      </div>
      <div class="legend-item-compact holiday">
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
  justify-content: center;
  font-size: 0.8rem;
  color: white;
  font-weight: 700;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  min-width: 100px;
  text-align: center;
}

.legend-item-compact:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15), inset 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.legend-item-compact.available {
  background: linear-gradient(135deg, #10b981, #059669);
}

.legend-item-compact.half {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.legend-item-compact.unavailable {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.legend-item-compact.holiday {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.legend-item-compact.unknown {
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
  color: #4b5563;
}


</style>
