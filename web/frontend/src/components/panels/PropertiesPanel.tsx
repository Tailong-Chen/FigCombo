import { useState } from 'react'
import { Type, Image as ImageIcon, BarChart3, Layers, Settings, Trash2, Copy, Move, Maximize } from 'lucide-react'
import { useFigureStore, selectSelectedPanel } from '../../stores/index'
import type { Panel, ImagePanel, PlotPanel, AnnotationPanel } from '../types/index'
import toast from 'react-hot-toast'

interface PanelTypeConfig {
  icon: typeof Type
  label: string
  color: string
}

const panelTypeConfig: Record<string, PanelTypeConfig> = {
  image: { icon: ImageIcon, label: 'Image Panel', color: 'text-accent-purple' },
  plot: { icon: BarChart3, label: 'Plot Panel', color: 'text-scientific-600' },
  composite: { icon: Layers, label: 'Composite Panel', color: 'text-accent-teal' },
  annotation: { icon: Type, label: 'Text Annotation', color: 'text-gray-600' },
}

export default function PropertiesPanel() {
  const selectedPanel = useFigureStore(selectSelectedPanel)
  const { updatePanel, removePanel, selectPanel, panels } = useFigureStore()

  if (!selectedPanel) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <Settings className="w-12 h-12 text-gray-300 mb-4" />
        <h3 className="text-sm font-medium text-gray-900 mb-1">No Panel Selected</h3>
        <p className="text-xs text-gray-500">
          Click on a panel in the preview to edit its properties
        </p>
      </div>
    )
  }

  const config = panelTypeConfig[selectedPanel.type] || panelTypeConfig.annotation
  const Icon = config.icon

  const handlePositionChange = (axis: 'x' | 'y', value: number) => {
    updatePanel(selectedPanel.id, {
      position: { ...selectedPanel.position, [axis]: value },
    })
  }

  const handleSizeChange = (dimension: 'width' | 'height', value: number) => {
    updatePanel(selectedPanel.id, {
      size: { ...selectedPanel.size, [dimension]: value },
    })
  }

  const handleDelete = () => {
    removePanel(selectedPanel.id)
    selectPanel(null)
    toast.success('Panel removed')
  }

  const handleDuplicate = () => {
    const newPanel = {
      ...selectedPanel,
      id: crypto.randomUUID(),
      position: {
        x: selectedPanel.position.x + 5,
        y: selectedPanel.position.y + 5,
      },
      zIndex: panels.length,
    }
    useFigureStore.getState().addPanel(newPanel)
    toast.success('Panel duplicated')
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-gray-50 ${config.color}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-gray-900 truncate">{config.label}</h3>
            <p className="text-xs text-gray-500">ID: {selectedPanel.id.slice(0, 8)}</p>
          </div>
        </div>
      </div>

      {/* Properties */}
      <div className="flex-1 overflow-auto p-4 space-y-6">
        {/* Label */}
        <div>
          <label className="label">Label</label>
          <input
            type="text"
            value={selectedPanel.label || ''}
            onChange={(e) => updatePanel(selectedPanel.id, { label: e.target.value })}
            placeholder="Panel label (e.g., A, B, C)"
            className="input"
          />
        </div>

        {/* Position */}
        <div>
          <label className="label flex items-center gap-2">
            <Move className="w-4 h-4" />
            Position (mm)
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-xs text-gray-500 mb-1 block">X</span>
              <input
                type="number"
                value={selectedPanel.position.x.toFixed(1)}
                onChange={(e) => handlePositionChange('x', parseFloat(e.target.value) || 0)}
                className="input"
                step="0.5"
              />
            </div>
            <div>
              <span className="text-xs text-gray-500 mb-1 block">Y</span>
              <input
                type="number"
                value={selectedPanel.position.y.toFixed(1)}
                onChange={(e) => handlePositionChange('y', parseFloat(e.target.value) || 0)}
                className="input"
                step="0.5"
              />
            </div>
          </div>
        </div>

        {/* Size */}
        <div>
          <label className="label flex items-center gap-2">
            <Maximize className="w-4 h-4" />
            Size (mm)
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-xs text-gray-500 mb-1 block">Width</span>
              <input
                type="number"
                value={selectedPanel.size.width.toFixed(1)}
                onChange={(e) => handleSizeChange('width', parseFloat(e.target.value) || 1)}
                className="input"
                min="1"
                step="0.5"
              />
            </div>
            <div>
              <span className="text-xs text-gray-500 mb-1 block">Height</span>
              <input
                type="number"
                value={selectedPanel.size.height.toFixed(1)}
                onChange={(e) => handleSizeChange('height', parseFloat(e.target.value) || 1)}
                className="input"
                min="1"
                step="0.5"
              />
            </div>
          </div>
        </div>

        {/* Type-specific properties */}
        {selectedPanel.type === 'image' && (
          <ImagePanelProperties panel={selectedPanel as ImagePanel} />
        )}
        {selectedPanel.type === 'plot' && (
          <PlotPanelProperties panel={selectedPanel as PlotPanel} />
        )}
        {selectedPanel.type === 'annotation' && (
          <AnnotationPanelProperties panel={selectedPanel as AnnotationPanel} />
        )}

        {/* Z-Index */}
        <div>
          <label className="label">Layer Order (Z-Index)</label>
          <input
            type="number"
            value={selectedPanel.zIndex}
            onChange={(e) => updatePanel(selectedPanel.id, { zIndex: parseInt(e.target.value, 10) || 0 })}
            className="input"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-gray-200 space-y-2">
        <button
          onClick={handleDuplicate}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          <Copy className="w-4 h-4" />
          Duplicate Panel
        </button>
        <button
          onClick={handleDelete}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Delete Panel
        </button>
      </div>
    </div>
  )
}

function ImagePanelProperties({ panel }: { panel: ImagePanel }) {
  const { updatePanel } = useFigureStore()

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-900 border-b border-gray-200 pb-2">Image Settings</h4>

      <div>
        <label className="label">Source URL</label>
        <input
          type="text"
          value={panel.src || ''}
          onChange={(e) => updatePanel(panel.id, { src: e.target.value })}
          placeholder="Enter image URL"
          className="input"
        />
      </div>

      <div>
        <label className="label">Brightness</label>
        <input
          type="range"
          min="0"
          max="200"
          value={panel.filters?.brightness || 100}
          onChange={(e) =>
            updatePanel(panel.id, {
              filters: { ...panel.filters, brightness: parseInt(e.target.value) },
            })
          }
          className="w-full"
        />
      </div>

      <div>
        <label className="label">Contrast</label>
        <input
          type="range"
          min="0"
          max="200"
          value={panel.filters?.contrast || 100}
          onChange={(e) =>
            updatePanel(panel.id, {
              filters: { ...panel.filters, contrast: parseInt(e.target.value) },
            })
          }
          className="w-full"
        />
      </div>
    </div>
  )
}

function PlotPanelProperties({ panel }: { panel: PlotPanel }) {
  const { updatePanel } = useFigureStore()

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-900 border-b border-gray-200 pb-2">Plot Settings</h4>

      <div>
        <label className="label">Plot Type</label>
        <select
          value={panel.plotType}
          onChange={(e) => updatePanel(panel.id, { plotType: e.target.value })}
          className="input"
        >
          <option value="bar-chart">Bar Chart</option>
          <option value="scatter-plot">Scatter Plot</option>
          <option value="line-chart">Line Chart</option>
          <option value="box-plot">Box Plot</option>
          <option value="heatmap">Heatmap</option>
        </select>
      </div>

      <div>
        <label className="label">Data Source</label>
        <textarea
          rows={3}
          placeholder="Enter data or select a file..."
          className="input resize-none"
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="show-grid"
          className="rounded border-gray-300 text-scientific-600 focus:ring-scientific-500"
        />
        <label htmlFor="show-grid" className="text-sm text-gray-700">Show Grid</label>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="show-legend"
          className="rounded border-gray-300 text-scientific-600 focus:ring-scientific-500"
        />
        <label htmlFor="show-legend" className="text-sm text-gray-700">Show Legend</label>
      </div>
    </div>
  )
}

function AnnotationPanelProperties({ panel }: { panel: AnnotationPanel }) {
  const { updatePanel } = useFigureStore()

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-900 border-b border-gray-200 pb-2">Text Settings</h4>

      <div>
        <label className="label">Content</label>
        <textarea
          rows={3}
          value={panel.content || ''}
          onChange={(e) => updatePanel(panel.id, { content: e.target.value })}
          placeholder="Enter text content..."
          className="input resize-none"
        />
      </div>

      <div>
        <label className="label">Font Size</label>
        <input
          type="number"
          value={panel.fontSize || 12}
          onChange={(e) => updatePanel(panel.id, { fontSize: parseInt(e.target.value, 10) })}
          className="input"
          min="6"
          max="72"
        />
      </div>

      <div>
        <label className="label">Color</label>
        <input
          type="color"
          value={panel.color || '#000000'}
          onChange={(e) => updatePanel(panel.id, { color: e.target.value })}
          className="w-full h-10 rounded-md border border-gray-300"
        />
      </div>

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={panel.bold || false}
            onChange={(e) => updatePanel(panel.id, { bold: e.target.checked })}
            className="rounded border-gray-300 text-scientific-600 focus:ring-scientific-500"
          />
          <span className="text-sm text-gray-700">Bold</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={panel.italic || false}
            onChange={(e) => updatePanel(panel.id, { italic: e.target.checked })}
            className="rounded border-gray-300 text-scientific-600 focus:ring-scientific-500"
          />
          <span className="text-sm text-gray-700">Italic</span>
        </label>
      </div>
    </div>
  )
}
