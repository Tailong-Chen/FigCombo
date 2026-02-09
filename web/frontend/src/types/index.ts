// Core Types for FigCombo Frontend

export interface Position {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Rectangle extends Position, Size {}

export interface PanelBase {
  id: string;
  type: PanelType;
  label?: string;
  position: Position;
  size: Size;
  zIndex: number;
}

export type PanelType =
  | 'image'
  | 'plot'
  | 'composite'
  | 'inset'
  | 'annotation';

export type PlotCategory =
  | 'statistics'
  | 'bioinformatics'
  | 'survival'
  | 'imaging'
  | 'molecular';

export interface PlotType {
  id: string;
  name: string;
  category: PlotCategory;
  description: string;
  icon: string;
  parameters: ParameterSchema[];
  thumbnail?: string;
}

export interface ParameterSchema {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'enum' | 'color';
  label: string;
  description?: string;
  required: boolean;
  default?: unknown;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}

export interface ImagePanel extends PanelBase {
  type: 'image';
  src: string;
  originalSize?: Size;
  crop?: Rectangle;
  filters?: ImageFilters;
}

export interface ImageFilters {
  brightness?: number;
  contrast?: number;
  saturation?: number;
  blur?: number;
}

export interface PlotPanel extends PanelBase {
  type: 'plot';
  plotType: string;
  data?: unknown;
  parameters: Record<string, unknown>;
  styleOverrides?: StyleOverrides;
}

export interface CompositePanel extends PanelBase {
  type: 'composite';
  layout: LayoutDefinition;
  children: Panel[];
}

export interface InsetPanel extends PanelBase {
  type: 'inset';
  parentId: string;
  anchor: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  content: Panel;
}

export interface AnnotationPanel extends PanelBase {
  type: 'annotation';
  content: string;
  fontSize?: number;
  fontFamily?: string;
  color?: string;
  bold?: boolean;
  italic?: boolean;
}

export type Panel = ImagePanel | PlotPanel | CompositePanel | InsetPanel | AnnotationPanel;

export interface LayoutDefinition {
  type: 'grid' | 'horizontal' | 'vertical' | 'free' | 'custom';
  rows?: number;
  cols?: number;
  gap?: number;
  padding?: number;
  code?: string;
}

export interface FigureState {
  id: string;
  name: string;
  width: number;
  height: number;
  dpi: number;
  layout: LayoutDefinition;
  panels: Panel[];
  selectedPanelId: string | null;
  backgroundColor: string;
  journalPreset: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface JournalPreset {
  id: string;
  name: string;
  description: string;
  maxWidth: number;
  maxHeight: number;
  maxPanels: number;
  dpi: number;
  colorMode: 'rgb' | 'cmyk';
  format: 'png' | 'pdf' | 'tiff';
}

export interface ExportOptions {
  format: 'png' | 'pdf' | 'svg' | 'tiff';
  dpi: number;
  colorMode: 'rgb' | 'cmyk' | 'grayscale';
  quality?: number;
  transparent: boolean;
  cropToContent: boolean;
}

export interface StyleOverrides {
  fontFamily?: string;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
  lineWidth?: number;
  markerSize?: number;
  gridVisible?: boolean;
  gridColor?: string;
  axisColor?: string;
  tickColor?: string;
}

export interface LayoutTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnail: string;
  layout: LayoutDefinition;
  defaultPanels: Partial<Panel>[];
}

export interface HistoryState {
  past: FigureState[];
  present: FigureState;
  future: FigureState[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PreviewState {
  zoom: number;
  pan: Position;
  showGrid: boolean;
  showLabels: boolean;
  snapToGrid: boolean;
  gridSize: number;
}

export interface DragItem {
  id: string;
  type: 'panel' | 'plot-type' | 'template';
  data: unknown;
}

export interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface AutoSaveState {
  lastSaved: Date | null;
  isSaving: boolean;
  hasUnsavedChanges: boolean;
}
