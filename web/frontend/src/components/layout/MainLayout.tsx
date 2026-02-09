import { Outlet, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { PanelLeft, PanelRight, Save, Undo2, Redo2, Download, FilePlus, FileText, Settings } from 'lucide-react'
import { useFigureStore, startAutoSave, stopAutoSave } from '../../stores/index'
import toast from 'react-hot-toast'
import FigurePreview from '../preview/FigurePreview'
import PropertiesPanel from '../panels/PropertiesPanel'
import ExportPanel from '../export/ExportPanel'
import Modal from '../common/Modal'

export default function MainLayout() {
  const [leftPanelOpen, setLeftPanelOpen] = useState(true)
  const [rightPanelOpen, setRightPanelOpen] = useState(true)
  const [showExportModal, setShowExportModal] = useState(false)

  const {
    name,
    autoSaveState,
    undo,
    redo,
    canUndo,
    canRedo,
    resetFigure,
    triggerAutoSave
  } = useFigureStore()

  useEffect(() => {
    startAutoSave(30000)
    return () => stopAutoSave()
  }, [])

  const handleSave = async () => {
    await triggerAutoSave()
    toast.success('Figure saved')
  }

  const handleNew = () => {
    if (confirm('Create a new figure? Unsaved changes will be lost.')) {
      resetFigure()
      toast.success('New figure created')
    }
  }

  const handleUndo = () => {
    undo()
  }

  const handleRedo = () => {
    redo()
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-scientific-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="3" width="7" height="7" rx="1" />
                <rect x="3" y="14" width="7" height="7" rx="1" />
                <rect x="14" y="14" width="7" height="7" rx="1" />
              </svg>
            </div>
            <h1 className="font-semibold text-gray-900">FigCombo</h1>
          </div>

          <div className="h-6 w-px bg-gray-300" />

          <div className="flex items-center gap-1">
            <button
              onClick={handleNew}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="New Figure"
            >
              <FilePlus className="w-4 h-4" />
            </button>
            <button
              onClick={handleUndo}
              disabled={!canUndo()}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-30"
              title="Undo"
            >
              <Undo2 className="w-4 h-4" />
            </button>
            <button
              onClick={handleRedo}
              disabled={!canRedo()}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-30"
              title="Redo"
            >
              <Redo2 className="w-4 h-4" />
            </button>
            <button
              onClick={handleSave}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="Save"
            >
              <Save className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500 truncate max-w-xs">{name}</span>
          {autoSaveState.hasUnsavedChanges && (
            <span className="text-xs text-amber-600">Unsaved</span>
          )}
          {autoSaveState.isSaving && (
            <span className="text-xs text-scientific-600">Saving...</span>
          )}
          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors">
            <Settings className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowExportModal(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-scientific-600 text-white text-sm rounded-md hover:bg-scientific-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel */}
        <aside
          className={`w-80 bg-white border-r border-gray-200 flex flex-col transition-all duration-200 ${
            !leftPanelOpen && '-ml-80'
          }`}
        >
          <Outlet />
        </aside>

        {/* Left Panel Toggle */}
        <button
          onClick={() => setLeftPanelOpen(!leftPanelOpen)}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-1.5 bg-white border border-gray-200 rounded-r-md shadow-sm hover:bg-gray-50 transition-colors"
          style={{ left: leftPanelOpen ? '320px' : '0' }}
        >
          <PanelLeft className={`w-4 h-4 text-gray-600 transition-transform ${!leftPanelOpen && 'rotate-180'}`} />
        </button>

        {/* Center - Preview Area */}
        <main className="flex-1 relative overflow-hidden">
          <FigurePreview />
        </main>

        {/* Right Panel Toggle */}
        <button
          onClick={() => setRightPanelOpen(!rightPanelOpen)}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 p-1.5 bg-white border border-gray-200 rounded-l-md shadow-sm hover:bg-gray-50 transition-colors"
          style={{ right: rightPanelOpen ? '320px' : '0' }}
        >
          <PanelRight className={`w-4 h-4 text-gray-600 transition-transform ${!rightPanelOpen && '-rotate-180'}`} />
        </button>

        {/* Right Panel */}
        <aside
          className={`w-80 bg-white border-l border-gray-200 flex flex-col transition-all duration-200 ${
            !rightPanelOpen && '-mr-80'
          }`}
        >
          <PropertiesPanel />
        </aside>
      </div>

      {/* Export Modal */}
      <Modal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        size="lg"
        showCloseButton={false}
      >
        <ExportPanel />
      </Modal>
    </div>
  )
}
