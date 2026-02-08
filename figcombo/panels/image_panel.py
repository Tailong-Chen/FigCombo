"""ImagePanel - display pre-rendered images (microscopy, blots, etc.)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import numpy as np
from matplotlib.axes import Axes

from figcombo.panels.base import BasePanel


class ImagePanel(BasePanel):
    """Panel that displays an existing image file.

    Supports PNG, TIFF, JPG, and other formats readable by PIL/matplotlib.

    Parameters
    ----------
    path : str or Path
        Path to the image file.
    trim : bool, optional
        If True, automatically trim white borders. Default False.
    scale_bar : str or None, optional
        If provided, add a scale bar with this label (e.g. '50 μm').
    scale_bar_length_frac : float, optional
        Length of scale bar as fraction of image width. Default 0.2.
    scale_bar_position : str, optional
        Position: 'bottom_right', 'bottom_left', 'top_right', 'top_left'.
        Default 'bottom_right'.
    scale_bar_color : str, optional
        Color of scale bar. Default 'white'.
    crop : tuple of float, optional
        Crop region as (left, top, right, bottom) fractions [0, 1].
    brightness : float, optional
        Brightness adjustment factor. 1.0 = no change. Default 1.0.
    contrast : float, optional
        Contrast adjustment factor. 1.0 = no change. Default 1.0.
    """

    def __init__(
        self,
        path: str | Path,
        trim: bool = False,
        scale_bar: str | None = None,
        scale_bar_length_frac: float = 0.2,
        scale_bar_position: str = 'bottom_right',
        scale_bar_color: str = 'white',
        crop: tuple[float, float, float, float] | None = None,
        brightness: float = 1.0,
        contrast: float = 1.0,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.path = Path(path)
        self.trim = trim
        self.scale_bar = scale_bar
        self.scale_bar_length_frac = scale_bar_length_frac
        self.scale_bar_position = scale_bar_position
        self.scale_bar_color = scale_bar_color
        self.crop = crop
        self.brightness = brightness
        self.contrast = contrast
        self._image_data: np.ndarray | None = None

    def _load_image(self) -> np.ndarray:
        """Load and preprocess the image."""
        from PIL import Image

        img = Image.open(self.path)

        # Convert to RGB if necessary
        if img.mode == 'RGBA':
            # Composite on white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Crop if specified
        if self.crop is not None:
            w, h = img.size
            left = int(self.crop[0] * w)
            top = int(self.crop[1] * h)
            right = int(self.crop[2] * w)
            bottom = int(self.crop[3] * h)
            img = img.crop((left, top, right, bottom))

        data = np.array(img, dtype=np.float32) / 255.0

        # Brightness / contrast
        if self.brightness != 1.0:
            data = np.clip(data * self.brightness, 0, 1)
        if self.contrast != 1.0:
            mean = data.mean()
            data = np.clip((data - mean) * self.contrast + mean, 0, 1)

        # Trim white borders
        if self.trim:
            data = self._trim_whitespace(data)

        return data

    @staticmethod
    def _trim_whitespace(img: np.ndarray, threshold: float = 0.95) -> np.ndarray:
        """Remove white borders from image array."""
        if img.ndim == 3:
            gray = img.mean(axis=2)
        else:
            gray = img

        # Find non-white rows and columns
        non_white_rows = np.where(gray.min(axis=1) < threshold)[0]
        non_white_cols = np.where(gray.min(axis=0) < threshold)[0]

        if len(non_white_rows) == 0 or len(non_white_cols) == 0:
            return img

        r_min, r_max = non_white_rows[0], non_white_rows[-1] + 1
        c_min, c_max = non_white_cols[0], non_white_cols[-1] + 1

        return img[r_min:r_max, c_min:c_max]

    def render(self, ax: Axes) -> None:
        """Render the image onto the axes."""
        if self._image_data is None:
            self._image_data = self._load_image()

        ax.imshow(self._image_data, aspect='equal')
        ax.set_axis_off()

        # Add scale bar if requested
        if self.scale_bar is not None:
            self._draw_scale_bar(ax)

    def _draw_scale_bar(self, ax: Axes) -> None:
        """Draw a scale bar on the image."""
        img_h, img_w = self._image_data.shape[:2]
        bar_length = int(img_w * self.scale_bar_length_frac)
        bar_height = max(2, int(img_h * 0.015))

        margin_x = int(img_w * 0.05)
        margin_y = int(img_h * 0.05)

        pos = self.scale_bar_position
        if 'right' in pos:
            x_start = img_w - margin_x - bar_length
        else:
            x_start = margin_x

        if 'bottom' in pos:
            y_start = img_h - margin_y - bar_height
        else:
            y_start = margin_y + bar_height

        # Draw bar
        from matplotlib.patches import Rectangle
        rect = Rectangle(
            (x_start, y_start), bar_length, bar_height,
            facecolor=self.scale_bar_color, edgecolor='none'
        )
        ax.add_patch(rect)

        # Draw label
        text_x = x_start + bar_length / 2
        text_y = y_start - bar_height * 1.5 if 'bottom' in pos else y_start + bar_height * 2.5
        ax.text(
            text_x, text_y, self.scale_bar,
            color=self.scale_bar_color,
            fontsize=7, fontweight='bold',
            ha='center', va='bottom' if 'bottom' in pos else 'top',
        )

    def get_preferred_aspect(self) -> Optional[float]:
        """Return image's native aspect ratio."""
        if self._image_data is None:
            try:
                self._image_data = self._load_image()
            except Exception:
                return None

        h, w = self._image_data.shape[:2]
        return w / h if h > 0 else None

    def validate(self) -> list[str]:
        errors = []
        if not self.path.exists():
            errors.append(f"Image file not found: {self.path}")
        if self.crop is not None:
            if len(self.crop) != 4:
                errors.append("crop must be a 4-tuple (left, top, right, bottom)")
            elif any(v < 0 or v > 1 for v in self.crop):
                errors.append("crop values must be in [0, 1]")
        return errors

    def __repr__(self) -> str:
        return f"ImagePanel('{self.path.name}')"
