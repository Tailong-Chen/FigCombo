import { useRef, useEffect, useState, useCallback } from 'react'
import { ZoomIn, ZoomOut, Maximize, Grid3X3, Move, MousePointer2 } from 'lucide-react'
import { useFigureStore, usePreviewStore } from '../../stores/index'
import type { Position, Panel } from '../types/index'
import { snapToGrid } from '../../utils/helpers'

export default function FigurePreview() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState<Position>({ x: 0, y: 0 })
  const [dragPanelId, setDragPanelId] = useState<string | null>(null)

  const { width, height, panels, selectedPanelId, selectPanel, movePanel, updatePanel } = useFigureStore()
  const {
    zoom,
    pan,
    showGrid,
    gridSize,
    snapToGrid: snapEnabled,
    zoomIn,
    zoomOut,
    resetZoom,
    fitToScreen,
    setPan,
    toggleGrid,
    toggleSnapToGrid,
  } = usePreviewStore()

  // Calculate scale factor (mm to pixels)
  const mmToPx = useCallback((mm: number) => {
    // Base scale: 1mm = 4px at 100% zoom
    return mm * 4 * zoom
  }, [zoom])

  const pxToMm = useCallback((px: number) => {
    return px / (4 * zoom)
  }, [zoom])

  // Handle pan
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === containerRef.current || (e.target as HTMLElement).dataset.role === 'canvas') {
      setIsDragging(true)
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && !dragPanelId) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setDragPanelId(null)
  }

  // Handle panel drag
  const handlePanelMouseDown = (e: React.MouseEvent, panelId: string) => {
    e.stopPropagation()
    selectPanel(panelId)
    setDragPanelId(panelId)
    setDragStart({ x: e.clientX, y: e.clientY })
  }

  const handlePanelMouseMove = (e: React.MouseEvent) => {
    if (dragPanelId) {
      const deltaX = pxToMm(e.clientX - dragStart.x)
      const deltaY = pxToMm(e.clientY - dragStart.y)

      const panel = panels.find(p => p.id === dragPanelId)
      if (panel) {
        let newX = panel.position.x + deltaX
        let newY = panel.position.y + deltaY

        if (snapEnabled) {
          newX = snapToGrid(newX, gridSize)
          newY = snapToGrid(newY, gridSize)
        }

        movePanel(dragPanelId, { x: newX, y: newY })
      }

      setDragStart({ x: e.clientX, y: e.clientY })
    }
  }

  // Fit to screen on mount
  useEffect(() => {
    if (containerRef.current) {
      const { clientWidth, clientHeight } = containerRef.current
      fitToScreen(clientWidth, clientHeight, width, height)
    }
  }, [])

  const figureWidthPx = mmToPx(width)
  const figureHeightPx = mmToPx(height)

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200">
        <div className="flex items-center gap-1">
          <button
            onClick={zoomOut}
            className="p-1.5 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-600 min-w-[60px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={zoomIn}
            className="p-1.5 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <div className="w-px h-4 bg-gray-300 mx-2" />
          <button
            onClick={() => containerRef.current && fitToScreen(
              containerRef.current.clientWidth,
              containerRef.current.clientHeight,
              width,
              height
            )}
            className="p-1.5 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            title="Fit to Screen"
          >
            <Maximize className="w-4 h-4" />
          </button>
          <button
            onClick={resetZoom}
            className="p-1.5 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            title="Reset Zoom"
          >
            <span className="text-xs font-medium">1:1</span>
          </button>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={toggleGrid}
            className={`flex items-center gap-1.5 px-2 py-1.5 text-sm rounded-md transition-colors ${
              showGrid ? 'bg-scientific-100 text-scientific-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Grid3X3 className="w-4 h-4" />
            Grid
          </button>
          <button
            onClick={toggleSnapToGrid}
            className={`flex items-center gap-1.5 px-2 py-1.5 text-sm rounded-md transition-colors ${
              snapEnabled ? 'bg-scientific-100 text-scientific-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <MousePointer2 className="w-4 h-4" />
            Snap
          </button>
        </div>
      </div>

      {/* Canvas Container */}
      <div
        ref={containerRef}
        className="flex-1 bg-gray-100 overflow-hidden relative cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={(e) => {
          handleMouseMove(e)
          handlePanelMouseMove(e)
        }}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Canvas */}
        <div
          data-role="canvas"
          className="absolute bg-white shadow-lg"
          style={{
            width: figureWidthPx,
            height: figureHeightPx,
            left: '50%',
            top: '50%',
            transform: `translate(-50%, -50%) translate(${pan.x}px, ${pan.y}px)`,
          }}
        >
          {/* Grid Overlay */}
          {showGrid && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage: `
                  linear-gradient(to right, rgba(14, 165, 233, 0.1) 1px, transparent 1px),
                  linear-gradient(to bottom, rgba(14, 165, 233, 0.1) 1px, transparent 1px)
                `,
                backgroundSize: `${mmToPx(gridSize)}px ${mmToPx(gridSize)}px`,
              }}
            />
          )}

          {/* Panels */}
          {panels.map((panel) => (
            <PanelPreview
              key={panel.id}
              panel={panel}
              isSelected={panel.id === selectedPanelId}
              mmToPx={mmToPx}
              onMouseDown={(e) => handlePanelMouseDown(e, panel.id)}
            />
          ))}

          {/* Dimensions Label */}
          <div className="absolute -bottom-6 left-0 right-0 text-center text-xs text-gray-500">
            {width} x {height} mm
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between px-4 py-1.5 bg-white border-t border-gray-200 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{panels.length} panel{panels.length !== 1 ? 's' : ''}</span>
          {selectedPanelId && (
            <span className="text-scientific-600">
              Selected: {panels.find(p => p.id === selectedPanelId)?.label || 'Unlabeled'}
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <span>DPI: {useFigureStore.getState().dpi}</span>
          <span>{width}mm x {height}mm</span>
        </div>
      </div>
    </div>
  )
}

interface PanelPreviewProps {
  panel: Panel
  isSelected: boolean
  mmToPx: (mm: number) => number
  onMouseDown: (e: React.MouseEvent) => void
}

function PanelPreview({ panel, isSelected, mmToPx, onMouseDown }: PanelPreviewProps) {
  const width = mmToPx(panel.size.width)
  const height = mmToPx(panel.size.height)
  const left = mmToPx(panel.position.x)
  const top = mmToPx(panel.position.y)

  const getPanelContent = () => {
    switch (panel.type) {
      case 'image':
        return (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <span className="text-gray-400 text-xs">Image</span>
          </div>
        )
      case 'plot':
        return (
          <div className="w-full h-full bg-scientific-50 flex items-center justify-center">
            <span className="text-scientific-400 text-xs">Plot</span>
          </div>
        )
      case 'annotation':
        return (
          <div className="w-full h-full flex items-center justify-center p-2">
            <span className="text-gray-600 text-xs text-center line-clamp-3">
              {(panel as { content?: string }).content || 'Text'}
            </span>
          </div>
        )
      default:
        return (
          <div className="w-full h-full bg-gray-50 flex items-center justify-center">
            <span className="text-gray-400 text-xs">Panel</span>
          </div>
        )
    }
  }

  return (
    <div
      className={`absolute cursor-move transition-shadow ${
        isSelected ? 'ring-2 ring-scientific-500 z-50' : 'hover:ring-1 hover:ring-gray-300'
      }`}
      style={{
        width,
        height,
        left,
        top,
        zIndex: panel.zIndex,
      }}
      onMouseDown={onMouseDown}
    >
      {/* Panel Content */}
      <div className="w-full h-full overflow-hidden rounded-sm">
        {getPanelContent()}
      </div>

      {/* Selection Handles */}
      {isSelected && (
        <>
          <div className="absolute -top-1 -left-1 w-2 h-2 bg-scientific-500 rounded-full" />
          <div className="absolute -top-1 -right-1 w-2 h-2 bg-scientific-500 rounded-full" />
          <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-scientific-500 rounded-full" />
          <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-scientific-500 rounded-full" />
        </>
      )}

      {/* Label */}
      {panel.label && (
        <div className="absolute -top-5 left-0 text-xs font-semibold text-gray-700">
          {panel.label}
        </div>
      )}
    </div>
  )
}
