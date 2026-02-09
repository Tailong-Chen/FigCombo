import type { Position, Size, Rectangle } from '../types/index';

export const generateId = (): string => {
  return crypto.randomUUID();
};

export const clamp = (value: number, min: number, max: number): number => {
  return Math.max(min, Math.min(max, value));
};

export const snapToGrid = (value: number, gridSize: number): number => {
  return Math.round(value / gridSize) * gridSize;
};

export const snapPositionToGrid = (
  position: Position,
  gridSize: number
): Position => ({
  x: snapToGrid(position.x, gridSize),
  y: snapToGrid(position.y, gridSize),
});

export const snapSizeToGrid = (size: Size, gridSize: number): Size => ({
  width: Math.max(gridSize, snapToGrid(size.width, gridSize)),
  height: Math.max(gridSize, snapToGrid(size.height, gridSize)),
});

export const formatDimensions = (
  width: number,
  height: number,
  unit: 'mm' | 'cm' | 'in' | 'px' = 'mm'
): string => {
  return `${width.toFixed(1)} x ${height.toFixed(1)} ${unit}`;
};

export const pixelsToMm = (px: number, dpi: number): number => {
  return (px / dpi) * 25.4;
};

export const mmToPixels = (mm: number, dpi: number): number => {
  return (mm * dpi) / 25.4;
};

export const inchesToMm = (inches: number): number => {
  return inches * 25.4;
};

export const mmToInches = (mm: number): number => {
  return mm / 25.4;
};

export const calculateAspectRatio = (width: number, height: number): string => {
  const gcd = (a: number, b: number): number => {
    return b === 0 ? a : gcd(b, a % b);
  };
  const divisor = gcd(Math.round(width), Math.round(height));
  return `${Math.round(width) / divisor}:${Math.round(height) / divisor}`;
};

export const isPointInRect = (
  point: Position,
  rect: Rectangle
): boolean => {
  return (
    point.x >= rect.x &&
    point.x <= rect.x + rect.width &&
    point.y >= rect.y &&
    point.y <= rect.y + rect.height
  );
};

export const doRectsIntersect = (
  rect1: Rectangle,
  rect2: Rectangle
): boolean => {
  return (
    rect1.x < rect2.x + rect2.width &&
    rect1.x + rect1.width > rect2.x &&
    rect1.y < rect2.y + rect2.height &&
    rect1.y + rect1.height > rect2.y
  );
};

export const getIntersectionArea = (
  rect1: Rectangle,
  rect2: Rectangle
): number => {
  const xOverlap = Math.max(
    0,
    Math.min(rect1.x + rect1.width, rect2.x + rect2.width) -
      Math.max(rect1.x, rect2.x)
  );
  const yOverlap = Math.max(
    0,
    Math.min(rect1.y + rect1.height, rect2.y + rect2.height) -
      Math.max(rect1.y, rect2.y)
  );
  return xOverlap * yOverlap;
};

export const constrainRect = (
  rect: Rectangle,
  bounds: Rectangle
): Rectangle => {
  const x = clamp(rect.x, bounds.x, bounds.x + bounds.width - rect.width);
  const y = clamp(rect.y, bounds.y, bounds.y + bounds.height - rect.height);
  const width = clamp(rect.width, 1, bounds.x + bounds.width - x);
  const height = clamp(rect.height, 1, bounds.y + bounds.height - y);

  return { x, y, width, height };
};

export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

export const debounce = <T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

export const throttle = <T extends (...args: unknown[]) => unknown>(
  fn: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle = false;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

export const getFileExtension = (filename: string): string => {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
};

export const isValidImageFile = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp'];
  return validTypes.includes(file.type);
};

export const readFileAsDataURL = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export const getImageDimensions = (
  src: string
): Promise<{ width: number; height: number }> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.width, height: img.height });
    img.onerror = reject;
    img.src = src;
  });
};

export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
};

export const generateLayoutCode = (
  rows: number,
  cols: number,
  gap: number = 2
): string => {
  const panels: string[] = [];
  for (let i = 0; i < rows * cols; i++) {
    const row = Math.floor(i / cols);
    const col = i % cols;
    panels.push(`  [${row}, ${col}]: panel${i + 1}`);
  }
  return `layout: grid\nrows: ${rows}\ncols: ${cols}\ngap: ${gap}mm\n\npanels:\n${panels.join('\n')}`;
};

export const parseLayoutCode = (code: string): Record<string, unknown> | null => {
  try {
    const lines = code.split('\n').filter((line) => line.trim());
    const result: Record<string, unknown> = { panels: {} };

    let inPanelsSection = false;

    for (const line of lines) {
      const trimmed = line.trim();

      if (trimmed === 'panels:') {
        inPanelsSection = true;
        continue;
      }

      if (!inPanelsSection) {
        const [key, ...valueParts] = trimmed.split(':');
        const value = valueParts.join(':').trim();

        if (key && value) {
          if (key === 'rows' || key === 'cols' || key === 'gap') {
            result[key] = key === 'gap' ? parseFloat(value) : parseInt(value, 10);
          } else {
            result[key] = value;
          }
        }
      } else {
        const match = trimmed.match(/\[(\d+),\s*(\d+)\]:\s*(.+)/);
        if (match) {
          const row = parseInt(match[1], 10);
          const col = parseInt(match[2], 10);
          const panelName = match[3].trim();
          (result.panels as Record<string, string>)[`${row},${col}`] = panelName;
        }
      }
    }

    return result;
  } catch {
    return null;
  }
};
