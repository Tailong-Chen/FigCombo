import { useState } from 'react'
import { Download, FileImage, FileText, FileCode, FileType, Settings, Check, AlertCircle } from 'lucide-react'
import { useFigureStore } from '../../stores/index'
import type { ExportOptions, JournalPreset } from '../types/index'
import { apiClient } from '../../api/client'
import { downloadBlob } from '../../utils/helpers'
import toast from 'react-hot-toast'

type ExportFormat = 'png' | 'pdf' | 'svg' | 'tiff'

const formats: { id: ExportFormat; name: string; icon: typeof FileImage; description: string }[] = [
  { id: 'png', name: 'PNG', icon: FileImage, description: 'Best for web and presentations' },
  { id: 'pdf', name: 'PDF', icon: FileText, description: 'Vector format for publications' },
  { id: 'svg', name: 'SVG', icon: FileCode, description: 'Editable vector graphics' },
  { id: 'tiff', name: 'TIFF', icon: FileType, description: 'High-quality for print' },
]

const colorModes = [
  { id: 'rgb', name: 'RGB', description: 'For digital display' },
  { id: 'cmyk', name: 'CMYK', description: 'For print' },
  { id: 'grayscale', name: 'Grayscale', description: 'Black and white' },
]

const dpiOptions = [72, 150, 300, 600, 1200]

// Sample journal presets
const journalPresets: JournalPreset[] = [
  {
    id: 'nature',
    name: 'Nature',
    description: 'Nature journal figure requirements',
    maxWidth: 180,
    maxHeight: 240,
    maxPanels: 8,
    dpi: 300,
    colorMode: 'rgb',
    format: 'pdf',
  },
  {
    id: 'science',
    name: 'Science',
    description: 'Science journal figure requirements',
    maxWidth: 180,
    maxHeight: 240,
    maxPanels: 6,
    dpi: 300,
    colorMode: 'rgb',
    format: 'pdf',
  },
  {
    id: 'cell',
    name: 'Cell',
    description: 'Cell Press figure requirements',
    maxWidth: 190,
    maxHeight: 230,
    maxPanels: 8,
    dpi: 300,
    colorMode: 'cmyk',
    format: 'tiff',
  },
  {
    id: 'plos',
    name: 'PLOS',
    description: 'PLOS ONE figure requirements',
    maxWidth: 190,
    maxHeight: 230,
    maxPanels: 12,
    dpi: 300,
    colorMode: 'rgb',
    format: 'tiff',
  },
  {
    id: 'bmc',
    name: 'BMC',
    description: 'BioMed Central figure requirements',
    maxWidth: 180,
    maxHeight: 240,
    maxPanels: 10,
    dpi: 300,
    colorMode: 'rgb',
    format: 'png',
  },
]

export default function ExportPanel() {
  const { id: figureId, name, width, height, panels, dpi: figureDpi } = useFigureStore()

  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('pdf')
  const [selectedDpi, setSelectedDpi] = useState(figureDpi)
  const [colorMode, setColorMode] = useState<'rgb' | 'cmyk' | 'grayscale'>('rgb')
  const [transparent, setTransparent] = useState(false)
  const [cropToContent, setCropToContent] = useState(false)
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [isExporting, setIsExporting] = useState(false)

  const handlePresetSelect = (preset: JournalPreset) => {
    setSelectedPreset(preset.id)
    setSelectedDpi(preset.dpi)
    setColorMode(preset.colorMode)
    setSelectedFormat(preset.format as ExportFormat)
    toast.success(`Applied ${preset.name} preset`)
  }

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const options: ExportOptions = {
        format: selectedFormat,
        dpi: selectedDpi,
        colorMode,
        transparent,
        cropToContent,
      }

      const blob = await apiClient.exportFigure(figureId, options)
      const filename = `${name.replace(/\s+/g, '_')}.${selectedFormat}`
      downloadBlob(blob, filename)

      toast.success(`Exported as ${selectedFormat.toUpperCase()}`)
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  // Calculate file size estimate
  const estimatedSize = () => {
    const pixelsPerMm = selectedDpi / 25.4
    const totalPixels = width * pixelsPerMm * height * pixelsPerMm
    const bytesPerPixel = selectedFormat === 'png' ? 4 : selectedFormat === 'tiff' ? 6 : 3
    const sizeBytes = totalPixels * bytesPerPixel
    const sizeMB = sizeBytes / (1024 * 1024)
    return sizeMB.toFixed(1)
  }

  // Check for warnings
  const warnings = []
  if (selectedPreset) {
    const preset = journalPresets.find(p => p.id === selectedPreset)
    if (preset) {
      if (width > preset.maxWidth) {
        warnings.push(`Width exceeds ${preset.name} maximum (${preset.maxWidth}mm)`)
      }
      if (height > preset.maxHeight) {
        warnings.push(`Height exceeds ${preset.name} maximum (${preset.maxHeight}mm)`)
      }
      if (panels.length > preset.maxPanels) {
        warnings.push(`Panel count exceeds ${preset.name} maximum (${preset.maxPanels})`)
      }
    }
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Download className="w-5 h-5" />
          Export Figure
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 space-y-6">
        {/* Format Selection */}
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-3">Format</h3>
          <div className="grid grid-cols-2 gap-2">
            {formats.map((format) => {
              const Icon = format.icon
              return (
                <button
                  key={format.id}
                  onClick={() => setSelectedFormat(format.id)}
                  className={`flex flex-col items-center gap-2 p-3 rounded-lg border transition-all ${
                    selectedFormat === format.id
                      ? 'border-scientific-500 bg-scientific-50 text-scientific-700'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-6 h-6" />
                  <div className="text-center">
                    <div className="font-medium text-sm">{format.name}</div>
                    <div className="text-xs text-gray-500">{format.description}</div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* DPI Selection */}
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-3">Resolution (DPI)</h3>
          <div className="flex flex-wrap gap-2">
            {dpiOptions.map((dpi) => (
              <button
                key={dpi}
                onClick={() => setSelectedDpi(dpi)}
                className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                  selectedDpi === dpi
                    ? 'border-scientific-500 bg-scientific-50 text-scientific-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {dpi}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Higher DPI is better for print quality but increases file size
          </p>
        </div>

        {/* Color Mode */}
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-3">Color Mode</h3>
          <div className="space-y-2">
            {colorModes.map((mode) => (
              <label
                key={mode.id}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                  colorMode === mode.id
                    ? 'border-scientific-500 bg-scientific-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="colorMode"
                  value={mode.id}
                  checked={colorMode === mode.id}
                  onChange={(e) => setColorMode(e.target.value as typeof colorMode)}
                  className="text-scientific-600 focus:ring-scientific-500"
                />
                <div>
                  <div className="font-medium text-sm">{mode.name}</div>
                  <div className="text-xs text-gray-500">{mode.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Options */}
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-3">Options</h3>
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={transparent}
                onChange={(e) => setTransparent(e.target.checked)}
                className="rounded border-gray-300 text-scientific-600 focus:ring-scientific-500"
              />
              <span className="text-sm text-gray-700">Transparent background</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={cropToContent}
                onChange={(e) => setCropToContent(e.target.checked)}
                className="rounded border-gray-300 text-scientific-600 focus:ring-scientific-500"
              />
              <span className="text-sm text-gray-700">Crop to content</span>
            </label>
          </div>
        </div>

        {/* Journal Presets */}
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-3">Journal Presets</h3>
          <div className="space-y-2">
            {journalPresets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handlePresetSelect(preset)}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  selectedPreset === preset.id
                    ? 'border-scientific-500 bg-scientific-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">{preset.name}</div>
                    <div className="text-xs text-gray-500">{preset.description}</div>
                  </div>
                  {selectedPreset === preset.id && (
                    <Check className="w-4 h-4 text-scientific-600" />
                  )}
                </div>
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span>{preset.maxWidth}x{preset.maxHeight}mm</span>
                  <span>•</span>
                  <span>{preset.dpi} DPI</span>
                  <span>•</span>
                  <span>{preset.format.toUpperCase()}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-amber-800 mb-2">
              <AlertCircle className="w-4 h-4" />
              <span className="font-medium text-sm">Warnings</span>
            </div>
            <ul className="text-xs text-amber-700 space-y-1">
              {warnings.map((warning, i) => (
                <li key={i}>• {warning}</li>
              ))}
            </ul>
          </div>
        )}

        {/* File Info */}
        <div className="bg-gray-50 rounded-lg p-3 space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Dimensions</span>
            <span className="font-medium">{width} x {height} mm</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Panels</span>
            <span className="font-medium">{panels.length}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Est. Size</span>
            <span className="font-medium">~{estimatedSize()} MB</span>
          </div>
        </div>
      </div>

      {/* Export Button */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleExport}
          disabled={isExporting}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-scientific-600 text-white font-medium rounded-lg hover:bg-scientific-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isExporting ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              Export as {selectedFormat.toUpperCase()}
            </>
          )}
        </button>
      </div>
    </div>
  )
}
