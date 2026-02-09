import { useState, useCallback } from 'react'
import { Code, LayoutTemplate, Grid3X3, Rows3, Columns3, Maximize, Type } from 'lucide-react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { githubLight } from '@uiw/codemirror-theme-github'
import { useFigureStore } from '../../stores/index'
import { generateLayoutCode, parseLayoutCode } from '../../utils/helpers'
import toast from 'react-hot-toast'

const layoutTemplates = [
  { id: '1x1', name: 'Single Panel', rows: 1, cols: 1, icon: Maximize },
  { id: '1x2', name: '1x2 Grid', rows: 1, cols: 2, icon: Columns3 },
  { id: '2x1', name: '2x1 Grid', rows: 2, cols: 1, icon: Rows3 },
  { id: '2x2', name: '2x2 Grid', rows: 2, cols: 2, icon: Grid3X3 },
  { id: '2x3', name: '2x3 Grid', rows: 2, cols: 3, icon: Grid3X3 },
  { id: '3x2', name: '3x2 Grid', rows: 3, cols: 2, icon: Grid3X3 },
]

export default function LayoutEditor() {
  const [activeMode, setActiveMode] = useState<'visual' | 'code'>('visual')
  const { layout, setLayout, panels, updateFigure } = useFigureStore()

  const [code, setCode] = useState(() => generateLayoutCode(
    layout.rows || 1,
    layout.cols || 1,
    layout.gap || 2
  ))

  const handleTemplateSelect = (template: typeof layoutTemplates[0]) => {
    const newLayout = {
      type: 'grid' as const,
      rows: template.rows,
      cols: template.cols,
      gap: layout.gap || 2,
      padding: layout.padding || 5,
    }
    setLayout(newLayout)
    setCode(generateLayoutCode(template.rows, template.cols, newLayout.gap))
    toast.success(`Applied ${template.name} template`)
  }

  const handleCodeChange = useCallback((value: string) => {
    setCode(value)
    const parsed = parseLayoutCode(value)
    if (parsed) {
      setLayout({
        ...layout,
        ...parsed,
        type: 'grid',
      })
    }
  }, [layout, setLayout])

  const handleGapChange = (gap: number) => {
    updateLayout({ gap })
    setCode(generateLayoutCode(layout.rows || 1, layout.cols || 1, gap))
  }

  const handlePaddingChange = (padding: number) => {
    updateLayout({ padding })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Mode Toggle */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveMode('visual')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-medium transition-colors ${
            activeMode === 'visual'
              ? 'text-scientific-600 bg-scientific-50 border-b-2 border-scientific-600'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          <LayoutTemplate className="w-4 h-4" />
          Visual
        </button>
        <button
          onClick={() => setActiveMode('code')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-medium transition-colors ${
            activeMode === 'code'
              ? 'text-scientific-600 bg-scientific-50 border-b-2 border-scientific-600'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          <Code className="w-4 h-4" />
          Code
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeMode === 'visual' ? (
          <div className="p-4 space-y-6">
            {/* Templates */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Templates</h3>
              <div className="grid grid-cols-3 gap-2">
                {layoutTemplates.map((template) => {
                  const Icon = template.icon
                  const isActive = layout.rows === template.rows && layout.cols === template.cols
                  return (
                    <button
                      key={template.id}
                      onClick={() => handleTemplateSelect(template)}
                      className={`flex flex-col items-center gap-2 p-3 rounded-lg border transition-all ${
                        isActive
                          ? 'border-scientific-500 bg-scientific-50 text-scientific-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-xs">{template.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Grid Settings */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-gray-900">Grid Settings</h3>

              <div className="space-y-3">
                <div>
                  <label className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Gap</span>
                    <span>{layout.gap || 2}mm</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.5"
                    value={layout.gap || 2}
                    onChange={(e) => handleGapChange(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Padding</span>
                    <span>{layout.padding || 5}mm</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="20"
                    step="1"
                    value={layout.padding || 5}
                    onChange={(e) => handlePaddingChange(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm text-gray-600 mb-1 block">Rows</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={layout.rows || 1}
                      onChange={(e) => {
                        const rows = parseInt(e.target.value, 10)
                        setLayout({ ...layout, rows })
                        setCode(generateLayoutCode(rows, layout.cols || 1, layout.gap || 2))
                      }}
                      className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-600 mb-1 block">Columns</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={layout.cols || 1}
                      onChange={(e) => {
                        const cols = parseInt(e.target.value, 10)
                        setLayout({ ...layout, cols })
                        setCode(generateLayoutCode(layout.rows || 1, cols, layout.gap || 2))
                      }}
                      className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Current Layout Preview */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Current Layout</h3>
              <div
                className="aspect-video bg-gray-50 rounded-lg border border-gray-200 p-4"
                style={{
                  display: 'grid',
                  gridTemplateRows: `repeat(${layout.rows || 1}, 1fr)`,
                  gridTemplateColumns: `repeat(${layout.cols || 1}, 1fr)`,
                  gap: `${(layout.gap || 2) * 4}px`,
                }}
              >
                {Array.from({ length: (layout.rows || 1) * (layout.cols || 1) }).map((_, i) => (
                  <div
                    key={i}
                    className="bg-white rounded border-2 border-dashed border-gray-300 flex items-center justify-center"
                  >
                    <span className="text-xs text-gray-400">
                      {String.fromCharCode(65 + i)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Panel Count */}
            <div className="flex items-center justify-between py-3 border-t border-gray-200">
              <span className="text-sm text-gray-600">Panels</span>
              <span className="text-sm font-medium text-gray-900">{panels.length}</span>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col">
            <div className="flex-1 overflow-auto">
              <CodeMirror
                value={code}
                height="100%"
                theme={githubLight}
                extensions={[python()]}
                onChange={handleCodeChange}
                className="text-sm"
                basicSetup={{
                  lineNumbers: true,
                  highlightActiveLineGutter: true,
                  highlightActiveLine: true,
                  foldGutter: false,
                }}
              />
            </div>
            <div className="p-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
              Use grid syntax: rows, cols, gap, and panel positions
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
