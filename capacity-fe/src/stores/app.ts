import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ToastMessage } from '@/types'

export const useAppStore = defineStore('app', () => {
  // State
  const loading = ref(false)
  const toasts = ref<ToastMessage[]>([])
  const sidebar = ref({
    visible: false,
    collapsed: false,
  })

  // Actions
  function setLoading(isLoading: boolean) {
    loading.value = isLoading
  }

  function showToast(toast: Omit<ToastMessage, 'life'> & { life?: number }) {
    const newToast: ToastMessage = {
      life: 3000,
      ...toast,
    }
    toasts.value.push(newToast)
  }

  function showSuccess(summary: string, detail?: string) {
    showToast({
      severity: 'success',
      summary,
      detail,
    })
  }

  function showError(summary: string, detail?: string) {
    showToast({
      severity: 'error',
      summary,
      detail,
    })
  }

  function showInfo(summary: string, detail?: string) {
    showToast({
      severity: 'info',
      summary,
      detail,
    })
  }

  function showWarning(summary: string, detail?: string) {
    showToast({
      severity: 'warn',
      summary,
      detail,
    })
  }

  function removeToast(index: number) {
    toasts.value.splice(index, 1)
  }

  function clearToasts() {
    toasts.value = []
  }

  function toggleSidebar() {
    sidebar.value.visible = !sidebar.value.visible
  }

  function setSidebarVisible(visible: boolean) {
    sidebar.value.visible = visible
  }

  function toggleSidebarCollapsed() {
    sidebar.value.collapsed = !sidebar.value.collapsed
  }

  function setSidebarCollapsed(collapsed: boolean) {
    sidebar.value.collapsed = collapsed
  }

  return {
    // State
    loading,
    toasts,
    sidebar,

    // Actions
    setLoading,
    showToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    removeToast,
    clearToasts,
    toggleSidebar,
    setSidebarVisible,
    toggleSidebarCollapsed,
    setSidebarCollapsed,
  }
})
