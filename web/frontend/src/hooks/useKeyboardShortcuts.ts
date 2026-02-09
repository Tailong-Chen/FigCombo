import { useEffect, useCallback } from 'react'
import { useFigureStore } from '../../stores/index'

interface KeyboardShortcuts {
  onSave?: () => void
  onUndo?: () => void
  onRedo?: () => void
  onDelete?: () => void
  onDuplicate?: () => void
  onSelectAll?: () => void
  onEscape?: () => void
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcuts) {
  const { undo, redo, canUndo, canRedo, selectedPanelId, removePanel, selectPanel } = useFigureStore()

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const metaKey = isMac ? event.metaKey : event.ctrlKey

      // Save: Ctrl/Cmd + S
      if (metaKey && event.key === 's') {
        event.preventDefault()
        shortcuts.onSave?.()
      }

      // Undo: Ctrl/Cmd + Z
      if (metaKey && event.key === 'z' && !event.shiftKey) {
        event.preventDefault()
        if (canUndo()) {
          undo()
          shortcuts.onUndo?.()
        }
      }

      // Redo: Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y
      if ((metaKey && event.key === 'z' && event.shiftKey) || (metaKey && event.key === 'y')) {
        event.preventDefault()
        if (canRedo()) {
          redo()
          shortcuts.onRedo?.()
        }
      }

      // Delete: Delete key
      if (event.key === 'Delete' || event.key === 'Backspace') {
        if (selectedPanelId) {
          event.preventDefault()
          removePanel(selectedPanelId)
          selectPanel(null)
          shortcuts.onDelete?.()
        }
      }

      // Duplicate: Ctrl/Cmd + D
      if (metaKey && event.key === 'd') {
        event.preventDefault()
        shortcuts.onDuplicate?.()
      }

      // Select All: Ctrl/Cmd + A
      if (metaKey && event.key === 'a') {
        event.preventDefault()
        shortcuts.onSelectAll?.()
      }

      // Escape: Deselect
      if (event.key === 'Escape') {
        selectPanel(null)
        shortcuts.onEscape?.()
      }
    },
    [shortcuts, undo, redo, canUndo, canRedo, selectedPanelId, removePanel, selectPanel]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}
