import { useState, useCallback } from 'react'
import type { Position } from '../types/index'

interface DragState {
  isDragging: boolean
  startPosition: Position
  currentPosition: Position
  delta: Position
}

export function useDragAndDrop(onDragEnd?: (delta: Position) => void) {
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    startPosition: { x: 0, y: 0 },
    currentPosition: { x: 0, y: 0 },
    delta: { x: 0, y: 0 },
  })

  const handleDragStart = useCallback((position: Position) => {
    setDragState({
      isDragging: true,
      startPosition: position,
      currentPosition: position,
      delta: { x: 0, y: 0 },
    })
  }, [])

  const handleDragMove = useCallback((position: Position) => {
    setDragState((prev) => ({
      ...prev,
      currentPosition: position,
      delta: {
        x: position.x - prev.startPosition.x,
        y: position.y - prev.startPosition.y,
      },
    }))
  }, [])

  const handleDragEnd = useCallback(() => {
    onDragEnd?.(dragState.delta)
    setDragState((prev) => ({
      ...prev,
      isDragging: false,
      delta: { x: 0, y: 0 },
    }))
  }, [dragState.delta, onDragEnd])

  return {
    ...dragState,
    handleDragStart,
    handleDragMove,
    handleDragEnd,
  }
}
