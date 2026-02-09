import { useState, useMemo } from 'react'
import { Search, BarChart3, Dna, HeartPulse, Microscope, Atom, Filter, ChevronDown, Plus } from 'lucide-react'
import { useDraggable } from '@dnd-kit/core'
import type { PlotCategory, PlotType } from '../types/index'
import { useFigureStore } from '../../stores/index'
import toast from 'react-hot-toast'

const categories: { id: PlotCategory | 'all'; label: string; icon: typeof BarChart3; color: string }[] = [
  { id: 'all', label: 'All Types', icon: Filter, color: 'text-gray-600' },
  { id: 'statistics', label: 'Statistics', icon: BarChart3, color: 'text-scientific-600' },
  { id: 'bioinformatics', label: 'Bioinformatics', icon: Dna, color: 'text-accent-emerald' },
  { id: 'survival', label: 'Survival', icon: HeartPulse, color: 'text-accent-rose' },
  { id: 'imaging', label: 'Imaging', icon: Microscope, color: 'text-accent-purple' },
  { id: 'molecular', label: 'Molecular', icon: Atom, color: 'text-accent-teal' },
]

// Sample plot types - in production, these would come from the API
const samplePlotTypes: PlotType[] = [
  // Statistics
  { id: 'bar-chart', name: 'Bar Chart', category: 'statistics', description: 'Compare categorical data with bars', icon: 'BarChart', parameters: [] },
  { id: 'box-plot', name: 'Box Plot', category: 'statistics', description: 'Show data distribution with quartiles', icon: 'BoxPlot', parameters: [] },
  { id: 'violin-plot', name: 'Violin Plot', category: 'statistics', description: 'Combine box plot with kernel density', icon: 'Violin', parameters: [] },
  { id: 'scatter-plot', name: 'Scatter Plot', category: 'statistics', description: 'Show relationship between two variables', icon: 'Scatter', parameters: [] },
  { id: 'histogram', name: 'Histogram', category: 'statistics', description: 'Display data distribution', icon: 'Histogram', parameters: [] },
  { id: 'line-chart', name: 'Line Chart', category: 'statistics', description: 'Show trends over time or sequence', icon: 'LineChart', parameters: [] },
  { id: 'heatmap', name: 'Heatmap', category: 'statistics', description: 'Visualize matrix data with colors', icon: 'Heatmap', parameters: [] },
  { id: 'correlation-matrix', name: 'Correlation Matrix', category: 'statistics', description: 'Show correlation between variables', icon: 'Matrix', parameters: [] },

  // Bioinformatics
  { id: 'volcano-plot', name: 'Volcano Plot', category: 'bioinformatics', description: 'Visualize differential expression', icon: 'Volcano', parameters: [] },
  { id: 'ma-plot', name: 'MA Plot', category: 'bioinformatics', description: 'Log ratio vs mean average plot', icon: 'MAPlot', parameters: [] },
  { id: 'pca-plot', name: 'PCA Plot', category: 'bioinformatics', description: 'Principal component analysis', icon: 'PCA', parameters: [] },
  { id: 'pathway-diagram', name: 'Pathway Diagram', category: 'bioinformatics', description: 'Visualize biological pathways', icon: 'Pathway', parameters: [] },
  { id: 'sequence-logo', name: 'Sequence Logo', category: 'bioinformatics', description: 'Display sequence conservation', icon: 'Sequence', parameters: [] },
  { id: 'genome-browser', name: 'Genome Browser', category: 'bioinformatics', description: 'View genomic regions', icon: 'Genome', parameters: [] },

  // Survival
  { id: 'kaplan-meier', name: 'Kaplan-Meier', category: 'survival', description: 'Survival probability over time', icon: 'Survival', parameters: [] },
  { id: 'hazard-ratio', name: 'Hazard Ratio', category: 'survival', description: 'Forest plot of hazard ratios', icon: 'Forest', parameters: [] },
  { id: 'risk-table', name: 'Risk Table', category: 'survival', description: 'Number at risk over time', icon: 'RiskTable', parameters: [] },

  // Imaging
  { id: 'microscopy', name: 'Microscopy Image', category: 'imaging', description: 'Display microscopy images', icon: 'Microscope', parameters: [] },
  { id: 'mri-scan', name: 'MRI Scan', category: 'imaging', description: 'Medical imaging visualization', icon: 'MRI', parameters: [] },
  { id: 'histology', name: 'Histology', category: 'imaging', description: 'Tissue section images', icon: 'Histology', parameters: [] },
  { id: 'fluorescence', name: 'Fluorescence', category: 'imaging', description: 'Fluorescence microscopy', icon: 'Fluorescence', parameters: [] },

  // Molecular
  { id: 'protein-structure', name: 'Protein Structure', category: 'molecular', description: '3D protein visualization', icon: 'Protein', parameters: [] },
  { id: 'molecule-2d', name: '2D Molecule', category: 'molecular', description: '2D chemical structure', icon: 'Molecule2D', parameters: [] },
  { id: 'phylogenetic-tree', name: 'Phylogenetic Tree', category: 'molecular', description: 'Evolutionary relationships', icon: 'Tree', parameters: [] },
  { id: 'plasmid-map', name: 'Plasmid Map', category: 'molecular', description: 'Circular DNA visualization', icon: 'Plasmid', parameters: [] },
]

interface DraggablePlotCardProps {
  plotType: PlotType
  onAdd: () => void
}

function DraggablePlotCard({ plotType, onAdd }: DraggablePlotCardProps) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: `plot-${plotType.id}`,
    data: { type: 'plot-type', plotType },
  })

  const category = categories.find(c => c.id === plotType.category)
  const Icon = category?.icon || BarChart3

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className={`group relative bg-white rounded-lg border border-gray-200 p-3 cursor-grab hover:shadow-md transition-all ${
        isDragging ? 'opacity-50' : ''
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-md bg-gray-50 ${category?.color || 'text-gray-600'}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm text-gray-900 truncate">{plotType.name}</h4>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{plotType.description}</p>
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onAdd()
        }}
        className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-scientific-600 hover:bg-scientific-50 rounded-md opacity-0 group-hover:opacity-100 transition-all"
      >
        <Plus className="w-4 h-4" />
      </button>
    </div>
  )
}

export default function PanelLibrary() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<PlotCategory | 'all'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'category'>('name')
  const { addPanel } = useFigureStore()

  const filteredPlots = useMemo(() => {
    let plots = samplePlotTypes

    if (selectedCategory !== 'all') {
      plots = plots.filter(p => p.category === selectedCategory)
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      plots = plots.filter(
        p =>
          p.name.toLowerCase().includes(query) ||
          p.description.toLowerCase().includes(query)
      )
    }

    return plots.sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name)
      return a.category.localeCompare(b.category)
    })
  }, [searchQuery, selectedCategory, sortBy])

  const handleAddPanel = (plotType: PlotType) => {
    addPanel({
      type: 'plot',
      plotType: plotType.id,
      position: { x: 10, y: 10 },
      size: { width: 80, height: 60 },
      parameters: {},
    })
    toast.success(`Added ${plotType.name}`)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search and Filter */}
      <div className="p-4 border-b border-gray-200 space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search plot types..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-scientific-500 focus:border-scientific-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as PlotCategory | 'all')}
            className="flex-1 px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-scientific-500"
          >
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.label}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'name' | 'category')}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-scientific-500"
          >
            <option value="name">Name</option>
            <option value="category">Category</option>
          </select>
        </div>
      </div>

      {/* Category Pills */}
      <div className="px-4 py-3 border-b border-gray-200 overflow-x-auto scrollbar-thin">
        <div className="flex gap-2">
          {categories.slice(1).map((cat) => {
            const Icon = cat.icon
            const isActive = selectedCategory === cat.id
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(isActive ? 'all' : cat.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-scientific-100 text-scientific-700 border border-scientific-200'
                    : 'bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? cat.color : ''}`} />
                {cat.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Plot Types Grid */}
      <div className="flex-1 overflow-auto p-4">
        {filteredPlots.length === 0 ? (
          <div className="text-center py-8">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No plot types found</p>
            <p className="text-xs text-gray-400 mt-1">Try adjusting your search</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {filteredPlots.map((plotType) => (
              <DraggablePlotCard
                key={plotType.id}
                plotType={plotType}
                onAdd={() => handleAddPanel(plotType)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        <p className="text-xs text-gray-500 text-center">
          {filteredPlots.length} plot type{filteredPlots.length !== 1 ? 's' : ''} available
        </p>
      </div>
    </div>
  )
}
