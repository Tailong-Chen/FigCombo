import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { subscribeWithSelector } from 'zustand/middleware';
import type { FigureState, Panel, LayoutDefinition, HistoryState, AutoSaveState } from '../types/index';
import { apiClient } from '../../api/client';

const DEFAULT_FIGURE: FigureState = {
  id: crypto.randomUUID(),
  name: 'Untitled Figure',
  width: 180,
  height: 120,
  dpi: 300,
  layout: {
    type: 'grid',
    rows: 1,
    cols: 1,
    gap: 2,
    padding: 5,
  },
  panels: [],
  selectedPanelId: null,
  backgroundColor: '#ffffff',
  journalPreset: null,
  createdAt: new Date(),
  updatedAt: new Date(),
};

interface FigureActions {
  // History
  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;

  // Figure operations
  setFigure: (figure: FigureState) => void;
  updateFigure: (updates: Partial<FigureState>) => void;
  resetFigure: () => void;

  // Layout operations
  setLayout: (layout: LayoutDefinition) => void;
  updateLayout: (updates: Partial<LayoutDefinition>) => void;

  // Panel operations
  addPanel: (panel: Omit<Panel, 'id' | 'zIndex'> & { id?: string }) => void;
  updatePanel: (id: string, updates: Partial<Panel>) => void;
  removePanel: (id: string) => void;
  selectPanel: (id: string | null) => void;
  movePanel: (id: string, position: { x: number; y: number }) => void;
  resizePanel: (id: string, size: { width: number; height: number }) => void;
  reorderPanels: (panelIds: string[]) => void;
  bringToFront: (id: string) => void;
  sendToBack: (id: string) => void;

  // Auto-save
  autoSaveState: AutoSaveState;
  markAsSaving: () => void;
  markAsSaved: () => void;
  markAsUnsaved: () => void;
  triggerAutoSave: () => Promise<void>;
}

const MAX_HISTORY_SIZE = 50;

const createHistorySlice = (
  set: (fn: (state: FigureStore) => void) => void,
  get: () => FigureStore
) => ({
  history: {
    past: [],
    present: DEFAULT_FIGURE,
    future: [],
  } as HistoryState,

  saveToHistory: () => {
    const state = get();
    set((draft) => {
      const newPast = [...draft.history.past, draft.history.present].slice(-MAX_HISTORY_SIZE);
      draft.history.past = newPast;
      draft.history.present = { ...state } as FigureState;
      draft.history.future = [];
    });
  },

  undo: () => {
    set((draft) => {
      if (draft.history.past.length === 0) return;
      const previous = draft.history.past[draft.history.past.length - 1];
      const newPast = draft.history.past.slice(0, -1);
      draft.history.future = [draft.history.present, ...draft.history.future];
      draft.history.present = previous;
      draft.history.past = newPast;

      // Restore figure state from history
      Object.assign(draft, previous);
    });
  },

  redo: () => {
    set((draft) => {
      if (draft.history.future.length === 0) return;
      const next = draft.history.future[0];
      const newFuture = draft.history.future.slice(1);
      draft.history.past = [...draft.history.past, draft.history.present];
      draft.history.present = next;
      draft.history.future = newFuture;

      // Restore figure state from history
      Object.assign(draft, next);
    });
  },

  canUndo: () => get().history.past.length > 0,
  canRedo: () => get().history.future.length > 0,
});

type FigureStore = FigureState & FigureActions & ReturnType<typeof createHistorySlice>;

export const useFigureStore = create<FigureStore>()(
  subscribeWithSelector(
    immer((set, get) => ({
      ...DEFAULT_FIGURE,
      ...createHistorySlice(set, get),

      autoSaveState: {
        lastSaved: null,
        isSaving: false,
        hasUnsavedChanges: false,
      },

      // Figure operations
      setFigure: (figure) => {
        set((draft) => {
          Object.assign(draft, figure);
          draft.autoSaveState.hasUnsavedChanges = true;
        });
      },

      updateFigure: (updates) => {
        set((draft) => {
          Object.assign(draft, updates);
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = true;
        });
        get().saveToHistory();
      },

      resetFigure: () => {
        set((draft) => {
          Object.assign(draft, DEFAULT_FIGURE);
          draft.id = crypto.randomUUID();
          draft.createdAt = new Date();
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = false;
        });
        get().saveToHistory();
      },

      // Layout operations
      setLayout: (layout) => {
        set((draft) => {
          draft.layout = layout;
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = true;
        });
        get().saveToHistory();
      },

      updateLayout: (updates) => {
        set((draft) => {
          Object.assign(draft.layout, updates);
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = true;
        });
        get().saveToHistory();
      },

      // Panel operations
      addPanel: (panel) => {
        set((draft) => {
          const newPanel = {
            ...panel,
            id: panel.id || crypto.randomUUID(),
            zIndex: draft.panels.length,
          } as Panel;
          draft.panels.push(newPanel);
          draft.selectedPanelId = newPanel.id;
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = true;
        });
        get().saveToHistory();
      },

      updatePanel: (id, updates) => {
        set((draft) => {
          const panel = draft.panels.find((p) => p.id === id);
          if (panel) {
            Object.assign(panel, updates);
            draft.updatedAt = new Date();
            draft.autoSaveState.hasUnsavedChanges = true;
          }
        });
        get().saveToHistory();
      },

      removePanel: (id) => {
        set((draft) => {
          draft.panels = draft.panels.filter((p) => p.id !== id);
          if (draft.selectedPanelId === id) {
            draft.selectedPanelId = null;
          }
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = true;
        });
        get().saveToHistory();
      },

      selectPanel: (id) => {
        set((draft) => {
          draft.selectedPanelId = id;
        });
      },

      movePanel: (id, position) => {
        set((draft) => {
          const panel = draft.panels.find((p) => p.id === id);
          if (panel) {
            panel.position = position;
            draft.updatedAt = new Date();
            draft.autoSaveState.hasUnsavedChanges = true;
          }
        });
      },

      resizePanel: (id, size) => {
        set((draft) => {
          const panel = draft.panels.find((p) => p.id === id);
          if (panel) {
            panel.size = size;
            draft.updatedAt = new Date();
            draft.autoSaveState.hasUnsavedChanges = true;
          }
        });
      },

      reorderPanels: (panelIds) => {
        set((draft) => {
          const panelMap = new Map(draft.panels.map((p) => [p.id, p]));
          draft.panels = panelIds
            .map((id) => panelMap.get(id))
            .filter((p): p is Panel => p !== undefined);
          draft.updatedAt = new Date();
          draft.autoSaveState.hasUnsavedChanges = true;
        });
        get().saveToHistory();
      },

      bringToFront: (id) => {
        set((draft) => {
          const panel = draft.panels.find((p) => p.id === id);
          if (panel) {
            const maxZ = Math.max(...draft.panels.map((p) => p.zIndex), 0);
            panel.zIndex = maxZ + 1;
          }
        });
      },

      sendToBack: (id) => {
        set((draft) => {
          const panel = draft.panels.find((p) => p.id === id);
          if (panel) {
            const minZ = Math.min(...draft.panels.map((p) => p.zIndex), 0);
            panel.zIndex = minZ - 1;
          }
        });
      },

      // Auto-save
      markAsSaving: () => {
        set((draft) => {
          draft.autoSaveState.isSaving = true;
        });
      },

      markAsSaved: () => {
        set((draft) => {
          draft.autoSaveState.isSaving = false;
          draft.autoSaveState.lastSaved = new Date();
          draft.autoSaveState.hasUnsavedChanges = false;
        });
      },

      markAsUnsaved: () => {
        set((draft) => {
          draft.autoSaveState.hasUnsavedChanges = true;
        });
      },

      triggerAutoSave: async () => {
        const state = get();
        if (!state.autoSaveState.hasUnsavedChanges || state.autoSaveState.isSaving) {
          return;
        }

        state.markAsSaving();
        try {
          const figureData: FigureState = {
            id: state.id,
            name: state.name,
            width: state.width,
            height: state.height,
            dpi: state.dpi,
            layout: state.layout,
            panels: state.panels,
            selectedPanelId: state.selectedPanelId,
            backgroundColor: state.backgroundColor,
            journalPreset: state.journalPreset,
            createdAt: state.createdAt,
            updatedAt: state.updatedAt,
          };
          await apiClient.updateFigure(state.id, figureData);
          state.markAsSaved();
        } catch (error) {
          console.error('Auto-save failed:', error);
          state.markAsUnsaved();
        }
      },
    }))
  )
);

// Auto-save subscription
let autoSaveInterval: ReturnType<typeof setInterval> | null = null;

export const startAutoSave = (intervalMs = 30000) => {
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval);
  }
  autoSaveInterval = setInterval(() => {
    useFigureStore.getState().triggerAutoSave();
  }, intervalMs);
};

export const stopAutoSave = () => {
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval);
    autoSaveInterval = null;
  }
};

// Selectors
export const selectSelectedPanel = (state: FigureState) =>
  state.panels.find((p) => p.id === state.selectedPanelId);

export const selectPanelById = (state: FigureState, id: string) =>
  state.panels.find((p) => p.id === id);

export const selectPanelsByType = (state: FigureState, type: string) =>
  state.panels.filter((p) => p.type === type);

export default useFigureStore;
