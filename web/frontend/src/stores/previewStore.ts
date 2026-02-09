import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type { PreviewState, Position } from '../types/index';

interface PreviewActions {
  setZoom: (zoom: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  fitToScreen: (containerWidth: number, containerHeight: number, figureWidth: number, figureHeight: number) => void;

  setPan: (pan: Position) => void;
  panBy: (delta: Position) => void;
  resetPan: () => void;

  toggleGrid: () => void;
  setGridSize: (size: number) => void;
  toggleLabels: () => void;
  toggleSnapToGrid: () => void;

  resetPreview: () => void;
}

const DEFAULT_PREVIEW_STATE: PreviewState = {
  zoom: 1,
  pan: { x: 0, y: 0 },
  showGrid: true,
  showLabels: true,
  snapToGrid: false,
  gridSize: 10,
};

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 5;
const ZOOM_STEP = 0.1;

export const usePreviewStore = create<PreviewState & PreviewActions>()(
  immer((set, get) => ({
    ...DEFAULT_PREVIEW_STATE,

    setZoom: (zoom) => {
      set((draft) => {
        draft.zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom));
      });
    },

    zoomIn: () => {
      set((draft) => {
        draft.zoom = Math.min(MAX_ZOOM, draft.zoom + ZOOM_STEP);
      });
    },

    zoomOut: () => {
      set((draft) => {
        draft.zoom = Math.max(MIN_ZOOM, draft.zoom - ZOOM_STEP);
      });
    },

    resetZoom: () => {
      set((draft) => {
        draft.zoom = 1;
      });
    },

    fitToScreen: (containerWidth, containerHeight, figureWidth, figureHeight) => {
      set((draft) => {
        const padding = 40;
        const availableWidth = containerWidth - padding * 2;
        const availableHeight = containerHeight - padding * 2;

        const scaleX = availableWidth / figureWidth;
        const scaleY = availableHeight / figureHeight;

        draft.zoom = Math.min(scaleX, scaleY, 1);
        draft.pan = { x: 0, y: 0 };
      });
    },

    setPan: (pan) => {
      set((draft) => {
        draft.pan = pan;
      });
    },

    panBy: (delta) => {
      set((draft) => {
        draft.pan.x += delta.x;
        draft.pan.y += delta.y;
      });
    },

    resetPan: () => {
      set((draft) => {
        draft.pan = { x: 0, y: 0 };
      });
    },

    toggleGrid: () => {
      set((draft) => {
        draft.showGrid = !draft.showGrid;
      });
    },

    setGridSize: (size) => {
      set((draft) => {
        draft.gridSize = Math.max(1, Math.min(100, size));
      });
    },

    toggleLabels: () => {
      set((draft) => {
        draft.showLabels = !draft.showLabels;
      });
    },

    toggleSnapToGrid: () => {
      set((draft) => {
        draft.snapToGrid = !draft.snapToGrid;
      });
    },

    resetPreview: () => {
      set((draft) => {
        Object.assign(draft, DEFAULT_PREVIEW_STATE);
      });
    },
  }))
);

export default usePreviewStore;
