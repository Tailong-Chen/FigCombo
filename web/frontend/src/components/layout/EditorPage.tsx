import { useState } from 'react'
import { LayoutGrid, Library, Type, Image, Settings } from 'lucide-react'
import LayoutEditor from './LayoutEditor'
import PanelLibrary from '../panels/PanelLibrary'
import PropertiesPanel from '../panels/PropertiesPanel'
import ImageUpload from '../panels/ImageUpload'
import TextAnnotations from '../panels/TextAnnotations'
import { useFigureStore } from '../../stores/index'

const tabs = [
  { id: 'layout', label: 'Layout', icon: LayoutGrid },
  { id: 'panels', label: 'Panels', icon: Library },
  { id: 'text', label: 'Text', icon: Type },
  { id: 'images', label: 'Images', icon: Image },
  { id: 'settings', label: 'Settings', icon: Settings },
]

export default function EditorPage() {
  const [activeTab, setActiveTab] = useState('layout')
  const { width, height, dpi, backgroundColor, updateFigure, name } = useFigureStore()

  const renderContent = () => {
    switch (activeTab) {
      case 'layout':
        return <LayoutEditor />
      case 'panels':
        return <PanelLibrary />
      case 'text':
        return <TextAnnotations />
      case 'images':
        return <ImageUpload />
      case 'settings':
        return (
          <div className="p-4 space-y-6">
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Figure Information</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => updateFigure({ name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Dimensions</h3>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Width (mm)</label>
                  <input
                    type="number"
                    value={width}
                    onChange={(e) => updateFigure({ width: parseFloat(e.target.value) || 180 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    min="10"
                    max="500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Height (mm)</label>
                  <input
                    type="number"
                    value={height}
                    onChange={(e) => updateFigure({ height: parseFloat(e.target.value) || 120 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    min="10"
                    max="500"
                  />
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Resolution</h3>
              <div>
                <label className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>DPI</span>
                  <span>{dpi}</span>
                </label>
                <input
                  type="range"
                  min="72"
                  max="1200"
                  step="72"
                  value={dpi}
                  onChange={(e) => updateFigure({ dpi: parseInt(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>72</span>
                  <span>300</span>
                  <span>600</span>
                  <span>1200</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Appearance</h3>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Background Color</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={backgroundColor}
                    onChange={(e) => updateFigure({ backgroundColor: e.target.value })}
                    className="w-10 h-10 rounded-md border border-gray-300"
                  />
                  <input
                    type="text"
                    value={backgroundColor}
                    onChange={(e) => updateFigure({ backgroundColor: e.target.value })}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="bg-gray-50 rounded-lg p-3 space-y-1 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>Pixel Width:</span>
                  <span>{Math.round((width * dpi) / 25.4)}px</span>
                </div>
                <div className="flex justify-between">
                  <span>Pixel Height:</span>
                  <span>{Math.round((height * dpi) / 25.4)}px</span>
                </div>
                <div className="flex justify-between">
                  <span>Aspect Ratio:</span>
                  <span>{(width / height).toFixed(2)}:1</span>
                </div>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <>
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex flex-col items-center gap-1 py-3 px-2 text-xs font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-scientific-600 border-b-2 border-scientific-600 bg-scientific-50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto scrollbar-thin">
        {renderContent()}
      </div>
    </>
  )
}
