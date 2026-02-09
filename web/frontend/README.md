# FigCombo Frontend

A professional scientific figure composition tool built with React, TypeScript, and Tailwind CSS.

## Features

- **Layout Editor**: Visual and code-based layout editing with real-time preview
- **Panel Library**: Categorized scientific plot types with drag-and-drop support
- **Properties Panel**: Comprehensive panel configuration with JSON schema forms
- **Figure Preview**: Interactive preview with zoom, pan, and grid overlay
- **Export Panel**: Multiple format support (PNG, PDF, SVG, TIFF) with journal presets
- **State Management**: Zustand-based store with history/undo-redo and auto-save

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run type checking
npm run typecheck

# Run linting
npm run lint
```

## Project Structure

```
src/
├── components/
│   ├── common/          # Reusable UI components (Button, Input, Modal, etc.)
│   ├── layout/          # Layout editor and main layout components
│   ├── panels/          # Panel library and properties panel
│   ├── preview/         # Figure preview component
│   └── export/          # Export panel component
├── stores/              # Zustand state management
│   ├── figureStore.ts   # Main figure state with history
│   └── previewStore.ts  # Preview state (zoom, pan, grid)
├── hooks/               # Custom React hooks
├── types/               # TypeScript type definitions
├── api/                 # API client
└── utils/               # Utility functions
```

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand with Immer
- **Drag & Drop**: @dnd-kit
- **Code Editor**: CodeMirror 6
- **UI Components**: Headless UI, Lucide React
- **Notifications**: React Hot Toast

## API Integration

The frontend expects a REST API at the configured `VITE_API_URL` endpoint. See `src/api/client.ts` for the API interface.

## Development

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `VITE_API_URL`: Backend API URL
- `VITE_ENABLE_DEBUG_MODE`: Enable debug features

### Key Components

#### LayoutEditor
Located at `src/components/layout/LayoutEditor.tsx`
- Visual grid layout builder
- Code editor for layout definitions
- Template gallery

#### PanelLibrary
Located at `src/components/panels/PanelLibrary.tsx`
- Categorized plot types
- Search and filter
- Drag-and-drop support

#### FigurePreview
Located at `src/components/preview/FigurePreview.tsx`
- Interactive figure preview
- Zoom and pan controls
- Grid overlay
- Panel selection and dragging

#### ExportPanel
Located at `src/components/export/ExportPanel.tsx`
- Format selection
- DPI settings
- Journal presets
- File download

## License

MIT
