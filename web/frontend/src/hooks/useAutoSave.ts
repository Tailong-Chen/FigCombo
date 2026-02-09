import { useEffect, useCallback } from 'react'
import { useFigureStore } from '../../stores/index'

export function useAutoSave(intervalMs = 30000) {
  const { triggerAutoSave, autoSaveState } = useFigureStore()

  useEffect(() => {
    const interval = setInterval(() => {
      triggerAutoSave()
    }, intervalMs)

    return () => clearInterval(interval)
  }, [intervalMs, triggerAutoSave])

  const saveNow = useCallback(async () => {
    await triggerAutoSave()
  }, [triggerAutoSave])

  return {
    saveNow,
    lastSaved: autoSaveState.lastSaved,
    isSaving: autoSaveState.isSaving,
    hasUnsavedChanges: autoSaveState.hasUnsavedChanges,
  }
}
