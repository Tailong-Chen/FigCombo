import { useState, useEffect, useCallback } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://10.180.74.9:5000'

// Plot type definitions
const PLOT_TYPES = [
  { id: 'bar_plot', name: '条形图', category: '统计', icon: '📊' },
  { id: 'box_plot', name: '箱线图', category: '统计', icon: '📦' },
  { id: 'violin_plot', name: '小提琴图', category: '统计', icon: '🎻' },
  { id: 'scatter_plot', name: '散点图', category: '统计', icon: '⚫' },
  { id: 'histogram', name: '直方图', category: '统计', icon: '📊' },
  { id: 'line_plot', name: '折线图', category: '统计', icon: '📈' },
  { id: 'volcano_plot', name: '火山图', category: '生物信息', icon: '🌋' },
  { id: 'ma_plot', name: 'MA图', category: '生物信息', icon: '📉' },
  { id: 'heatmap', name: '热图', category: '生物信息', icon: '🔥' },
  { id: 'pca_plot', name: 'PCA图', category: '生物信息', icon: '🎯' },
  { id: 'kaplan_meier', name: '生存曲线', category: '生存分析', icon: '⏱️' },
  { id: 'sequence_logo', name: '序列Logo', category: '分子', icon: '🧬' },
]

// Nature Journal Layout Templates - All layouts are valid rectangular grids
const TEMPLATES = [
  // 基础布局 - 标准网格
  { name: '2x2 网格', code: 'ab/cd', desc: '经典四面板', category: '基础' },
  { name: '3x2 网格', code: 'abc/def', desc: '六面板标准布局', category: '基础' },
  { name: '2x3 网格', code: 'ab/cd/ef', desc: '六面板纵向', category: '基础' },
  { name: '4x2 网格', code: 'abcd/efgh', desc: '八面板密集布局', category: '基础' },
  { name: '2x4 网格', code: 'ab/cd/ef/gh', desc: '八面板纵向', category: '基础' },
  { name: '3x3 网格', code: 'abc/def/ghi', desc: '九面板显微图布局', category: '基础' },
  { name: '4x3 网格', code: 'abcd/efgh/ijk', desc: '十二面板大网格', category: '基础' },

  // Nature 主图布局 - 大图+小图组合（都是矩形）
  { name: 'Nature 大图+右2', code: 'aab/aac', desc: '左大+右2小', category: 'Nature主图' },
  { name: 'Nature 大图+下3', code: 'aaa/bcd', desc: '上大+下3小', category: 'Nature主图' },
  { name: 'Nature 双大对比', code: 'aa/bb', desc: 'WT vs Mutant对比', category: 'Nature主图' },
  { name: 'Nature 2大+2小', code: 'aabb/ccdd', desc: '2大图+2小图', category: 'Nature主图' },
  { name: 'Nature 左1右3', code: 'abbb/accc', desc: '左1+右3组合', category: 'Nature主图' },
  { name: 'Nature 上2下3', code: 'aab/ccc', desc: '上2+下3组合', category: 'Nature主图' },

  // Western Blot 布局
  { name: 'WB 双膜+2定量', code: 'aaaa/bbbb/cc/dd', desc: '双膜+2定量图', category: 'Western Blot' },
  { name: 'WB 3膜横向', code: 'aaa/bbb/ccc', desc: '3靶点横向', category: 'Western Blot' },
  { name: 'WB 2x2网格', code: 'aa/bb/cc/dd', desc: '4膜2x2网格', category: 'Western Blot' },

  // 显微图布局
  { name: '显微 2x2通道', code: 'ab/cd', desc: '4通道2x2', category: '显微图' },
  { name: '显微 2x3通道', code: 'ab/cd/ef', desc: '6通道2x3', category: '显微图' },
  { name: '显微 大图+右2', code: 'aab/aac', desc: '大图+2细节', category: '显微图' },

  // 生物信息学
  { name: '火山+MA 左1右1', code: 'aa/bb', desc: '差异表达2图', category: '生物信息' },
  { name: '热图+UMAP 2x2', code: 'ab/cd', desc: '单细胞4图', category: '生物信息' },
  { name: '基因组 3行轨道', code: 'aa/bb/cc', desc: '3轨道纵向', category: '生物信息' },

  // 补充图布局
  { name: '补充 4x2网格', code: 'abcd/efgh', desc: '8图密集补充', category: '补充图' },
  { name: '补充 3x2网格', code: 'abc/def', desc: '6图标准补充', category: '补充图' },
  { name: '补充 2x3网格', code: 'ab/cd/ef', desc: '6图纵向补充', category: '补充图' },

  // 复杂布局
  { name: '复杂 3行混合', code: 'aab/ccd/def', desc: '3行不同宽度', category: '复杂' },
  { name: '复杂 4行混合', code: 'aa/bc/def/ghi', desc: '4行递减', category: '复杂' },
]

interface PanelConfig {
  type: 'empty' | 'plot' | 'image' | 'text'
  plotType?: string
  title?: string
  data?: any
}

async function parseLayout(layout: string) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000)

  try {
    const res = await fetch(`${API_BASE}/api/layout/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ layout }),
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    return res.json()
  } catch (e) {
    clearTimeout(timeoutId)
    throw e
  }
}

async function generatePreview(config: any) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 30000)

  try {
    const res = await fetch(`${API_BASE}/api/figure/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    return res.json()
  } catch (e) {
    clearTimeout(timeoutId)
    throw e
  }
}

function App() {
  const [layoutCode, setLayoutCode] = useState('aab/aac/ddd')
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [panelConfigs, setPanelConfigs] = useState<Record<string, PanelConfig>>({})
  const [selectedPanel, setSelectedPanel] = useState<string | null>(null)
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [activeTab, setActiveTab] = useState<'layout' | 'preview'>('layout')

  const handleParse = useCallback(async () => {
    if (loading) return
    setLoading(true)
    setError('')
    setResult(null)
    setPreviewImage(null)

    try {
      const data = await parseLayout(layoutCode)
      if (data.success) {
        setResult(data)
        // Initialize panel configs
        const panels = data.grid?.panels || {}
        const configs: Record<string, PanelConfig> = {}
        Object.keys(panels).forEach(label => {
          configs[label] = panelConfigs[label] || { type: 'empty' }
        })
        setPanelConfigs(configs)
      } else {
        setError(data.error || '解析失败')
      }
    } catch (e: any) {
      setError(`请求失败: ${e.message}`)
    }
    setLoading(false)
  }, [layoutCode, loading, panelConfigs])

  const handleGeneratePreview = async () => {
    if (!result?.grid) {
      setError('请先解析布局')
      return
    }
    setGenerating(true)
    setError('')

    try {
      // Filter out empty panels for the API
      const panelsToSend: Record<string, PanelConfig> = {}
      Object.entries(panelConfigs).forEach(([label, config]) => {
        if (config.type !== 'empty') {
          panelsToSend[label] = config
        }
      })

      // Convert panel configs to API format (snake_case)
      const panelsForApi: Record<string, any> = {}
      Object.entries(panelsToSend).forEach(([label, config]) => {
        panelsForApi[label] = {
          type: config.type,
          plot_type: config.plotType,  // Convert camelCase to snake_case
          title: config.title
        }
      })

      const config = {
        layout: layoutCode,
        journal: 'nature',
        size: 'double',
        panels: panelsForApi
      }

      console.log('Sending config:', config)
      const data = await generatePreview(config)
      console.log('Received data:', data)

      if (data.success) {
        const imageUrl = data.preview || data.base64_image
        if (imageUrl) {
          setPreviewImage(imageUrl)
          setActiveTab('preview')
        } else {
          setError('返回数据中没有图片')
        }
      } else {
        setError(data.error || data.traceback || '生成失败')
      }
    } catch (e: any) {
      console.error('Generate preview error:', e)
      setError(`生成失败: ${e.message}`)
    }
    setGenerating(false)
  }

  const updatePanelConfig = (label: string, config: Partial<PanelConfig>) => {
    setPanelConfigs(prev => ({
      ...prev,
      [label]: { ...prev[label], ...config }
    }))
  }

  useEffect(() => {
    handleParse()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const grid = result?.grid
  const cellSize = 80 // Fixed cell size for square appearance

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">FigCombo - 科学图表组合工具</h1>
          <p className="text-sm opacity-80">为 Nature, Science, Cell 等期刊创建出版级多面板图表</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar */}
          <div className="lg:col-span-3 space-y-4">
            {/* Layout Input */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold mb-3">布局代码</h2>
              <textarea
                value={layoutCode}
                onChange={(e) => setLayoutCode(e.target.value)}
                className="w-full h-24 p-2 border rounded font-mono text-sm"
                placeholder="例如: aab/aac/ddd"
              />
              <button
                onClick={handleParse}
                disabled={loading}
                className="mt-2 w-full px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
              >
                {loading ? '解析中...' : '解析布局'}
              </button>
              {error && (
                <div className="mt-2 p-2 bg-red-50 text-red-600 text-sm rounded">{error}</div>
              )}
            </div>

            {/* Templates */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold mb-3">快速模板 ({TEMPLATES.length}个)</h2>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {['基础', 'Nature主图', 'Western Blot', '显微图', '生物信息', '补充图', '复杂'].map(category => {
                  const categoryTemplates = TEMPLATES.filter(t => t.category === category)
                  if (categoryTemplates.length === 0) return null
                  return (
                    <div key={category}>
                      <div className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">{category}</div>
                      <div className="space-y-1">
                        {categoryTemplates.map(t => (
                          <button
                            key={t.name}
                            onClick={() => {
                              setLayoutCode(t.code)
                              setTimeout(handleParse, 100)
                            }}
                            className="w-full text-left p-2 hover:bg-blue-50 rounded text-sm border border-gray-200 transition-colors"
                          >
                            <div className="font-medium text-gray-800">{t.name}</div>
                            <div className="text-xs text-gray-500">{t.desc}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-6">
            {/* Tabs */}
            <div className="bg-white rounded-lg shadow mb-4">
              <div className="flex border-b">
                <button
                  onClick={() => setActiveTab('layout')}
                  className={`px-4 py-2 ${activeTab === 'layout' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
                >
                  布局设计
                </button>
                <button
                  onClick={() => setActiveTab('preview')}
                  className={`px-4 py-2 ${activeTab === 'preview' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
                >
                  图表预览
                </button>
              </div>

              <div className="p-4">
                {activeTab === 'layout' ? (
                  grid ? (
                    <div>
                      <p className="text-sm text-gray-600 mb-4">
                        {grid.nrows} 行 × {grid.ncols} 列 | {grid.num_panels} 个面板
                        (点击面板配置图表)
                      </p>

                      {/* Square Grid Preview */}
                      <div
                        className="inline-grid gap-2 bg-gray-100 p-4 rounded"
                        style={{
                          gridTemplateColumns: `repeat(${grid.ncols}, ${cellSize}px)`,
                          gridTemplateRows: `repeat(${grid.nrows}, ${cellSize}px)`,
                        }}
                      >
                        {Object.entries(grid.panels || {}).map(([label, pos]: [string, any]) => {
                          const config = panelConfigs[label]
                          const isSelected = selectedPanel === label
                          return (
                            <div
                              key={label}
                              onClick={() => setSelectedPanel(label)}
                              className={`
                                rounded flex flex-col items-center justify-center font-bold cursor-pointer
                                transition-all hover:scale-105
                                ${isSelected ? 'ring-2 ring-yellow-400' : ''}
                                ${config?.type === 'plot' ? 'bg-green-500' :
                                  config?.type === 'image' ? 'bg-purple-500' :
                                  config?.type === 'text' ? 'bg-orange-500' : 'bg-blue-500'}
                                text-white
                              `}
                              style={{
                                gridRow: `${pos.row + 1} / span ${pos.rowspan}`,
                                gridColumn: `${pos.col + 1} / span ${pos.colspan}`,
                              }}
                            >
                              <span className="text-lg">{label.toUpperCase()}</span>
                              {config?.plotType && (
                                <span className="text-xs mt-1 opacity-80">
                                  {PLOT_TYPES.find(p => p.id === config.plotType)?.name || config.plotType}
                                </span>
                              )}
                            </div>
                          )
                        })}
                      </div>

                      {/* Generate Button */}
                      <button
                        onClick={handleGeneratePreview}
                        disabled={generating}
                        className="mt-4 w-full px-4 py-3 bg-green-600 text-white rounded-lg font-medium disabled:opacity-50"
                      >
                        {generating ? '生成中...' : '🎨 生成图表预览'}
                      </button>
                    </div>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-400">
                      <div className="text-center">
                        <div className="text-4xl mb-2">📊</div>
                        <p>输入布局代码并点击"解析布局"</p>
                      </div>
                    </div>
                  )
                ) : (
                  <div>
                    {previewImage ? (
                      <img
                        src={previewImage}
                        alt="预览"
                        className="max-w-full border rounded shadow"
                      />
                    ) : (
                      <div className="h-64 flex items-center justify-center text-gray-400">
                        <div className="text-center">
                          <div className="text-4xl mb-2">🖼️</div>
                          <p>点击"生成图表预览"查看结果</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Syntax Help */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 mb-2">布局语法</h3>
              <div className="grid grid-cols-2 gap-2 text-sm text-blue-700">
                <div><code className="bg-blue-100 px-1">aab/aac/ddd</code> - 基础网格</div>
                <div><code className="bg-blue-100 px-1">[top:ab/cd]</code> - 命名区域</div>
                <div><code className="bg-blue-100 px-1">a[i,ii,iii]</code> - 子面板</div>
                <div><code className="bg-blue-100 px-1">a{'{0.7,0.7,0.2,0.2}'}</code> - 嵌入图</div>
              </div>
            </div>
          </div>

          {/* Right Sidebar - Panel Configuration */}
          <div className="lg:col-span-3">
            {selectedPanel ? (
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="text-lg font-semibold mb-3">
                  面板 {selectedPanel.toUpperCase()} 配置
                </h2>

                {/* Panel Type */}
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">类型</label>
                  <select
                    value={panelConfigs[selectedPanel]?.type || 'empty'}
                    onChange={(e) => updatePanelConfig(selectedPanel, { type: e.target.value as any })}
                    className="w-full p-2 border rounded"
                  >
                    <option value="empty">空面板</option>
                    <option value="plot">数据图表</option>
                    <option value="image">图片</option>
                    <option value="text">文本</option>
                  </select>
                </div>

                {/* Plot Type Selection */}
                {panelConfigs[selectedPanel]?.type === 'plot' && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">图表类型</label>
                    <div className="space-y-1 max-h-64 overflow-y-auto">
                      {PLOT_TYPES.map(pt => (
                        <button
                          key={pt.id}
                          onClick={() => updatePanelConfig(selectedPanel, { plotType: pt.id })}
                          className={`
                            w-full text-left p-2 rounded text-sm
                            ${panelConfigs[selectedPanel]?.plotType === pt.id
                              ? 'bg-blue-100 border-blue-500 border'
                              : 'hover:bg-gray-100 border'}
                          `}
                        >
                          <span className="mr-2">{pt.icon}</span>
                          <span className="font-medium">{pt.name}</span>
                          <span className="text-xs text-gray-500 ml-2">({pt.category})</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Title Input */}
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">标题</label>
                  <input
                    type="text"
                    value={panelConfigs[selectedPanel]?.title || ''}
                    onChange={(e) => updatePanelConfig(selectedPanel, { title: e.target.value })}
                    className="w-full p-2 border rounded"
                    placeholder="输入标题"
                  />
                </div>

                <button
                  onClick={() => setSelectedPanel(null)}
                  className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded"
                >
                  关闭
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-4 text-gray-500 text-center">
                <div className="text-4xl mb-2">👆</div>
                <p>点击布局中的面板进行配置</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
