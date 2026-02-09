"""ImagePanel - display pre-rendered images (microscopy, blots, etc.)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union, Literal

import numpy as np
from matplotlib.axes import Axes

from figcombo.panels.base import BasePanel


class ImagePanel(BasePanel):
    """Panel that displays an existing image file with advanced processing options.

    Supports PNG, TIFF, JPG, and other formats readable by PIL/matplotlib.
    Provides comprehensive image processing capabilities including contrast
    enhancement, color mapping, geometric transformations, and annotations.

    Parameters
    ----------
    path : str or Path
        Path to the image file.
    trim : bool, optional
        If True, automatically trim white borders. Default False.
    scale_bar : str or None, optional
        If provided, add a scale bar with this label (e.g. '50 μm').
        Can include physical length and units for automatic calculation.
    scale_bar_length_frac : float, optional
        Length of scale bar as fraction of image width. Default 0.2.
    scale_bar_position : str, optional
        Position: 'bottom_right', 'bottom_left', 'top_right', 'top_left'.
        Default 'bottom_right'.
    scale_bar_color : str, optional
        Color of scale bar. Default 'white'.
    scale_bar_style : str, optional
        Style of scale bar: 'bar' (filled rectangle) or 'line' (horizontal line).
        Default 'bar'.
    scale_bar_bg : bool, optional
        If True, add semi-transparent background behind scale bar for readability.
        Default False.
    scale_bar_bg_alpha : float, optional
        Alpha transparency of scale bar background (0-1). Default 0.5.
    pixel_size : float or None, optional
        Size of one pixel in physical units (e.g., μm/pixel). Used with scale_bar
        to calculate actual physical length. If None, scale_bar is used as label only.
    crop : tuple of float, optional
        Crop region as (left, top, right, bottom) fractions [0, 1].
    brightness : float, optional
        Brightness adjustment factor. 1.0 = no change. Default 1.0.
    contrast : float, optional
        Contrast adjustment factor. 1.0 = no change. Default 1.0.
    auto_contrast : bool or str, optional
        If True, automatically adjust contrast using 'percentile' method.
        Can also specify method: 'percentile', 'histogram', 'adaptive'.
        Default False.
    auto_contrast_cutoff : tuple, optional
        Lower and upper percentile cutoffs for auto_contrast.
        Default (2, 98).
    colormap : str or None, optional
        Colormap to apply to grayscale images. Uses matplotlib colormaps.
        Examples: 'viridis', 'plasma', 'hot', 'cool', 'jet', 'gray'.
        If None, no colormap is applied. Default None.
    rotation : int, optional
        Rotation angle in degrees. Must be one of 0, 90, 180, 270.
        Default 0 (no rotation).
    flip_h : bool, optional
        If True, flip image horizontally. Default False.
    flip_v : bool, optional
        If True, flip image vertically. Default False.
    channel : int or str or None, optional
        For multi-channel images, specify which channel to display.
        Can be channel index (int) or channel name (str) like 'red', 'green', 'blue'.
        If None, all channels are displayed (for RGB) or first channel (for multi-channel).
        Default None.
    channel_axis : int, optional
        Axis containing channel data for multi-channel images. Default -1 (last axis).
    annotations : list of dict, optional
        List of annotation dictionaries. Each dict can specify:
        - type: 'text', 'arrow', 'circle', 'rectangle', 'line', 'point'
        - x, y: Position (in pixels or relative coordinates 0-1)
        - text: Text content (for text annotations)
        - color: Annotation color
        - fontsize: Font size for text
        - arrow_direction: (dx, dy) for arrows
        - size: Size of marker/shape
        - relative: If True, x/y are relative coordinates (0-1). Default True.
    roi : list of dict or None, optional
        Region of interest to highlight. Each dict specifies:
        - x, y: Top-left corner (pixels or relative)
        - width, height: ROI dimensions
        - color: Highlight color
        - linewidth: Border width
        - alpha: Fill transparency
        - relative: If True, coordinates are relative (0-1). Default True.
    gamma : float, optional
        Gamma correction factor. 1.0 = no change. Default 1.0.

    Examples
    --------
    >>> # Basic image display
    >>> panel = ImagePanel('image.png')

    >>> # With scale bar and auto contrast
    >>> panel = ImagePanel(
    ...     'microscope.tif',
    ...     scale_bar='50 μm',
    ...     pixel_size=0.5,  # 0.5 μm per pixel
    ...     auto_contrast=True,
    ...     scale_bar_style='bar'
    ... )

    >>> # Pseudo-color for fluorescence
    >>> panel = ImagePanel(
    ...     'dapi_channel.tif',
    ...     colormap='hot',
    ...     auto_contrast=True,
    ...     scale_bar='20 μm',
    ...     pixel_size=0.3
    ... )

    >>> # With annotations and ROI
    >>> panel = ImagePanel(
    ...     'cell_image.png',
    ...     annotations=[
    ...         {'type': 'arrow', 'x': 0.5, 'y': 0.5, 'arrow_direction': (0.1, 0.1),
    ...          'color': 'red', 'relative': True},
    ...         {'type': 'text', 'x': 0.6, 'y': 0.6, 'text': 'Nucleus',
    ...          'color': 'yellow', 'fontsize': 12}
    ...     ],
    ...     roi=[{'x': 100, 'y': 100, 'width': 200, 'height': 200,
    ...           'color': 'green', 'linewidth': 2, 'relative': False}]
    ... )

    >>> # Multi-channel microscopy - show specific channel
    >>> panel = ImagePanel(
    ...     'multichannel.czi',
    ...     channel=1,  # Show second channel
    ...     colormap='green',
    ...     auto_contrast=True
    ... )
    """

    # Valid rotation angles
    VALID_ROTATIONS = (0, 90, 180, 270)

    # Channel name mappings
    CHANNEL_NAMES = {
        'red': 0, 'r': 0,
        'green': 1, 'g': 1,
        'blue': 2, 'b': 2,
        'alpha': 3, 'a': 3,
    }

    def __init__(
        self,
        path: str | Path,
        trim: bool = False,
        scale_bar: str | None = None,
        scale_bar_length_frac: float = 0.2,
        scale_bar_position: str = 'bottom_right',
        scale_bar_color: str = 'white',
        scale_bar_style: Literal['bar', 'line'] = 'bar',
        scale_bar_bg: bool = False,
        scale_bar_bg_alpha: float = 0.5,
        pixel_size: float | None = None,
        crop: tuple[float, float, float, float] | None = None,
        brightness: float = 1.0,
        contrast: float = 1.0,
        auto_contrast: bool | str = False,
        auto_contrast_cutoff: tuple[float, float] = (2, 98),
        colormap: str | None = None,
        rotation: int = 0,
        flip_h: bool = False,
        flip_v: bool = False,
        channel: int | str | None = None,
        channel_axis: int = -1,
        annotations: list[dict] | None = None,
        roi: list[dict] | None = None,
        gamma: float = 1.0,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.path = Path(path)
        self.trim = trim
        self.scale_bar = scale_bar
        self.scale_bar_length_frac = scale_bar_length_frac
        self.scale_bar_position = scale_bar_position
        self.scale_bar_color = scale_bar_color
        self.scale_bar_style = scale_bar_style
        self.scale_bar_bg = scale_bar_bg
        self.scale_bar_bg_alpha = scale_bar_bg_alpha
        self.pixel_size = pixel_size
        self.crop = crop
        self.brightness = brightness
        self.contrast = contrast
        self.auto_contrast = auto_contrast
        self.auto_contrast_cutoff = auto_contrast_cutoff
        self.colormap = colormap
        self.rotation = rotation
        self.flip_h = flip_h
        self.flip_v = flip_v
        self.channel = channel
        self.channel_axis = channel_axis
        self.annotations = annotations or []
        self.roi = roi or []
        self.gamma = gamma
        self._image_data: np.ndarray | None = None
        self._original_shape: tuple | None = None

    def _load_image(self) -> np.ndarray:
        """Load and preprocess the image."""
        from PIL import Image

        img = Image.open(self.path)
        self._original_shape = (img.height, img.width)

        # Handle multi-channel images (like TIFF with multiple pages/channels)
        if hasattr(img, 'n_frames') and img.n_frames > 1:
            # Multi-frame TIFF
            frames = []
            for i in range(img.n_frames):
                img.seek(i)
                frames.append(np.array(img.convert('L'), dtype=np.float32))
            data = np.stack(frames, axis=-1)
        else:
            # Standard image loading
            if img.mode == 'RGBA':
                # Composite on white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
                data = np.array(img, dtype=np.float32) / 255.0
            elif img.mode in ('L', 'I;16', 'I;8'):
                # Grayscale or 16-bit images
                data = np.array(img, dtype=np.float32)
                # Normalize to 0-1
                if data.max() > 1:
                    data = data / data.max()
            elif img.mode == 'RGB':
                data = np.array(img, dtype=np.float32) / 255.0
            else:
                img = img.convert('RGB')
                data = np.array(img, dtype=np.float32) / 255.0

        # Ensure data is at least 2D
        if data.ndim == 2:
            data = data[..., np.newaxis]

        # Handle channel selection for multi-channel images
        if self.channel is not None:
            data = self._select_channel(data)

        # Crop if specified
        if self.crop is not None:
            data = self._apply_crop(data)

        # Apply geometric transformations
        data = self._apply_transforms(data)

        # Apply image enhancements
        data = self._apply_enhancements(data)

        # Apply colormap if specified (for grayscale images)
        if self.colormap is not None:
            data = self._apply_colormap(data)

        # Trim white borders
        if self.trim:
            data = self._trim_whitespace(data)

        return data

    def _select_channel(self, data: np.ndarray) -> np.ndarray:
        """Select specific channel from multi-channel image."""
        # Determine channel index
        if isinstance(self.channel, str):
            channel_idx = self.CHANNEL_NAMES.get(self.channel.lower(), 0)
        else:
            channel_idx = self.channel

        # Handle different channel axis positions
        if data.ndim == 3:
            axis = self.channel_axis % data.ndim
            if data.shape[axis] > 1:
                # Multi-channel image
                if axis == 0:
                    data = data[channel_idx]
                elif axis == -1 or axis == 2:
                    data = data[..., channel_idx]
                else:
                    data = data.take(channel_idx, axis=axis)
            elif data.shape[axis] == 1:
                # Single channel, squeeze it
                data = np.squeeze(data, axis=axis)
        elif data.ndim == 4:
            # Handle 4D data (e.g., time-series multi-channel)
            axis = self.channel_axis % data.ndim
            data = data.take(channel_idx, axis=axis)

        # Ensure 2D or 3D
        if data.ndim == 2:
            data = data[..., np.newaxis]

        return data

    def _apply_crop(self, data: np.ndarray) -> np.ndarray:
        """Apply crop region to image data."""
        h, w = data.shape[:2]
        left = int(self.crop[0] * w)
        top = int(self.crop[1] * h)
        right = int(self.crop[2] * w)
        bottom = int(self.crop[3] * h)

        # Ensure valid crop region
        left = max(0, min(left, w - 1))
        top = max(0, min(top, h - 1))
        right = max(left + 1, min(right, w))
        bottom = max(top + 1, min(bottom, h))

        return data[top:bottom, left:right]

    def _apply_transforms(self, data: np.ndarray) -> np.ndarray:
        """Apply geometric transformations (rotation, flip)."""
        # Validate rotation
        if self.rotation not in self.VALID_ROTATIONS:
            raise ValueError(f"rotation must be one of {self.VALID_ROTATIONS}")

        # Apply rotation
        if self.rotation == 90:
            data = np.rot90(data, k=1)
        elif self.rotation == 180:
            data = np.rot90(data, k=2)
        elif self.rotation == 270:
            data = np.rot90(data, k=3)

        # Apply flips
        if self.flip_h:
            data = np.fliplr(data)
        if self.flip_v:
            data = np.flipud(data)

        return data

    def _apply_enhancements(self, data: np.ndarray) -> np.ndarray:
        """Apply brightness, contrast, gamma, and auto-contrast adjustments."""
        # Auto contrast
        if self.auto_contrast:
            data = self._apply_auto_contrast(data)

        # Brightness
        if self.brightness != 1.0:
            data = np.clip(data * self.brightness, 0, 1)

        # Contrast
        if self.contrast != 1.0:
            mean = data.mean()
            data = np.clip((data - mean) * self.contrast + mean, 0, 1)

        # Gamma correction
        if self.gamma != 1.0:
            data = np.clip(np.power(data, self.gamma), 0, 1)

        return data

    def _apply_auto_contrast(self, data: np.ndarray) -> np.ndarray:
        """Apply automatic contrast enhancement."""
        method = self.auto_contrast if isinstance(self.auto_contrast, str) else 'percentile'

        if method == 'percentile':
            return self._percentile_stretch(data)
        elif method == 'histogram':
            return self._histogram_equalization(data)
        elif method == 'adaptive':
            return self._adaptive_histogram_equalization(data)
        else:
            return self._percentile_stretch(data)

    def _percentile_stretch(self, data: np.ndarray) -> np.ndarray:
        """Apply percentile-based contrast stretching."""
        low, high = self.auto_contrast_cutoff

        if data.ndim == 3 and data.shape[2] in (3, 4):
            # Color image - process each channel
            result = np.zeros_like(data)
            for i in range(data.shape[2]):
                channel = data[..., i]
                p_low, p_high = np.percentile(channel, [low, high])
                if p_high > p_low:
                    result[..., i] = np.clip((channel - p_low) / (p_high - p_low), 0, 1)
                else:
                    result[..., i] = channel
            return result
        else:
            # Grayscale or single channel
            p_low, p_high = np.percentile(data, [low, high])
            if p_high > p_low:
                return np.clip((data - p_low) / (p_high - p_low), 0, 1)
            return data

    def _histogram_equalization(self, data: np.ndarray) -> np.ndarray:
        """Apply histogram equalization."""
        from PIL import ImageOps
        from PIL import Image

        if data.ndim == 3 and data.shape[2] == 1:
            data = data[..., 0]

        if data.ndim == 2:
            # Convert to 0-255 range for PIL
            img_8bit = (data * 255).astype(np.uint8)
            img = Image.fromarray(img_8bit, mode='L')
            img_eq = ImageOps.equalize(img)
            return np.array(img_eq, dtype=np.float32) / 255.0
        elif data.ndim == 3 and data.shape[2] in (3, 4):
            # For RGB, convert to HSV, equalize V channel
            import matplotlib.colors as mcolors
            hsv = mcolors.rgb_to_hsv(data[..., :3])
            img_8bit = (hsv[..., 2] * 255).astype(np.uint8)
            img = Image.fromarray(img_8bit, mode='L')
            img_eq = ImageOps.equalize(img)
            hsv[..., 2] = np.array(img_eq, dtype=np.float32) / 255.0
            return mcolors.hsv_to_rgb(hsv)
        return data

    def _adaptive_histogram_equalization(self, data: np.ndarray) -> np.ndarray:
        """Apply adaptive histogram equalization (CLAHE)."""
        try:
            from skimage.exposure import equalize_adapthist

            if data.ndim == 3 and data.shape[2] == 1:
                data = data[..., 0]

            if data.ndim == 2:
                return equalize_adapthist(data, clip_limit=0.03)
            elif data.ndim == 3 and data.shape[2] in (3, 4):
                # Apply to each channel separately
                result = np.zeros_like(data[..., :3])
                for i in range(3):
                    result[..., i] = equalize_adapthist(data[..., i], clip_limit=0.03)
                return result
        except ImportError:
            # Fallback to regular histogram equalization
            return self._histogram_equalization(data)
        return data

    def _apply_colormap(self, data: np.ndarray) -> np.ndarray:
        """Apply colormap to grayscale image."""
        import matplotlib.pyplot as plt

        # Extract single channel if needed
        if data.ndim == 3:
            if data.shape[2] == 1:
                data = data[..., 0]
            elif data.shape[2] in (3, 4):
                # Already RGB, convert to grayscale first
                data = data[..., :3].mean(axis=2)
            else:
                data = data[..., 0]

        # Ensure 2D
        if data.ndim > 2:
            data = data[..., 0]

        # Apply colormap
        cmap = plt.get_cmap(self.colormap)
        colored = cmap(data)

        # Remove alpha channel
        return colored[..., :3]

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

        # Draw ROI highlights
        if self.roi:
            self._draw_rois(ax)

        # Draw annotations
        if self.annotations:
            self._draw_annotations(ax)

    def _draw_scale_bar(self, ax: Axes) -> None:
        """Draw a scale bar on the image with enhanced options."""
        from matplotlib.patches import Rectangle, FancyBboxPatch

        img_h, img_w = self._image_data.shape[:2]

        # Calculate scale bar length
        if self.pixel_size is not None and self.scale_bar:
            # Parse physical length from scale_bar string
            physical_length = self._parse_physical_length(self.scale_bar)
            if physical_length is not None:
                # Calculate pixels needed for this physical length
                bar_length_pixels = physical_length / self.pixel_size
                # Ensure it's not too large
                bar_length_pixels = min(bar_length_pixels, img_w * 0.4)
            else:
                bar_length_pixels = int(img_w * self.scale_bar_length_frac)
        else:
            bar_length_pixels = int(img_w * self.scale_bar_length_frac)

        bar_height = max(2, int(img_h * 0.015))
        margin_x = int(img_w * 0.05)
        margin_y = int(img_h * 0.05)

        pos = self.scale_bar_position
        if 'right' in pos:
            x_start = img_w - margin_x - bar_length_pixels
        else:
            x_start = margin_x

        if 'bottom' in pos:
            y_start = img_h - margin_y - bar_height
            text_y_offset = -bar_height * 1.5
            va = 'bottom'
        else:
            y_start = margin_y
            text_y_offset = bar_height * 2.5
            va = 'top'

        # Draw background if requested
        if self.scale_bar_bg:
            bg_padding = 5
            bg_width = bar_length_pixels + 2 * bg_padding
            bg_height = bar_height + 40  # Extra space for text
            bg_x = x_start - bg_padding
            bg_y = y_start - bg_padding if 'bottom' in pos else y_start - 25

            bg_rect = FancyBboxPatch(
                (bg_x, bg_y), bg_width, bg_height,
                boxstyle="round,pad=0.01,rounding_size=2",
                facecolor='black', edgecolor='none',
                alpha=self.scale_bar_bg_alpha,
                transform=ax.transData
            )
            ax.add_patch(bg_rect)

        # Draw scale bar
        if self.scale_bar_style == 'line':
            # Draw line style
            line_y = y_start + bar_height / 2
            ax.plot([x_start, x_start + bar_length_pixels],
                   [line_y, line_y],
                   color=self.scale_bar_color, linewidth=3,
                   solid_capstyle='butt')
            # Add end caps
            cap_size = bar_height / 2
            ax.plot([x_start, x_start], [line_y - cap_size, line_y + cap_size],
                   color=self.scale_bar_color, linewidth=2)
            ax.plot([x_start + bar_length_pixels, x_start + bar_length_pixels],
                   [line_y - cap_size, line_y + cap_size],
                   color=self.scale_bar_color, linewidth=2)
        else:
            # Draw bar style (filled rectangle)
            rect = Rectangle(
                (x_start, y_start), bar_length_pixels, bar_height,
                facecolor=self.scale_bar_color, edgecolor='none'
            )
            ax.add_patch(rect)

        # Draw label
        text_x = x_start + bar_length_pixels / 2
        text_y = y_start + text_y_offset
        ax.text(
            text_x, text_y, self.scale_bar,
            color=self.scale_bar_color,
            fontsize=7, fontweight='bold',
            ha='center', va=va,
        )

    def _parse_physical_length(self, scale_bar_str: str) -> float | None:
        """Parse physical length from scale bar string.

        Examples:
            '50 μm' -> 50.0
            '100um' -> 100.0
            '1 mm' -> 1000.0 (converted to μm)
            '500 nm' -> 0.5 (converted to μm)
        """
        import re

        # Extract number and unit
        match = re.match(r'^([\d.]+)\s*(\w+)$', scale_bar_str.strip())
        if not match:
            return None

        try:
            value = float(match.group(1))
            unit = match.group(2).lower()
        except (ValueError, IndexError):
            return None

        # Convert to base unit (μm)
        unit_conversions = {
            'nm': 0.001,
            'um': 1.0, 'μm': 1.0, 'micron': 1.0, 'microns': 1.0,
            'mm': 1000.0,
            'cm': 10000.0,
        }

        conversion = unit_conversions.get(unit, 1.0)
        return value * conversion

    def _draw_rois(self, ax: Axes) -> None:
        """Draw ROI highlights on the image."""
        from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
        from matplotlib.collections import PatchCollection

        img_h, img_w = self._image_data.shape[:2]

        for roi in self.roi:
            # Get ROI parameters
            x = roi.get('x', 0)
            y = roi.get('y', 0)
            width = roi.get('width', 50)
            height = roi.get('height', 50)
            color = roi.get('color', 'red')
            linewidth = roi.get('linewidth', 2)
            alpha = roi.get('alpha', 0.0)  # Fill transparency
            relative = roi.get('relative', True)
            style = roi.get('style', 'rectangle')  # rectangle, circle, rounded

            # Convert relative to absolute coordinates
            if relative:
                x = x * img_w
                y = y * img_h
                width = width * img_w if width <= 1 else width
                height = height * img_h if height <= 1 else height

            # Adjust y coordinate (matplotlib uses bottom-left origin)
            y = img_h - y - height

            if style == 'circle':
                radius = max(width, height) / 2
                center_x = x + width / 2
                center_y = y + height / 2
                circle = Circle((center_x, center_y), radius,
                               facecolor=color, edgecolor=color,
                               alpha=alpha, linewidth=linewidth,
                               fill=alpha > 0)
                ax.add_patch(circle)
            elif style == 'rounded':
                rect = FancyBboxPatch(
                    (x, y), width, height,
                    boxstyle="round,pad=0.02,rounding_size=0.02*max(width,height)",
                    facecolor=color, edgecolor=color,
                    alpha=alpha, linewidth=linewidth,
                    fill=alpha > 0
                )
                ax.add_patch(rect)
            else:
                # Rectangle
                rect = Rectangle(
                    (x, y), width, height,
                    facecolor=color, edgecolor=color,
                    alpha=alpha, linewidth=linewidth,
                    fill=alpha > 0
                )
                ax.add_patch(rect)

    def _draw_annotations(self, ax: Axes) -> None:
        """Draw annotations on the image."""
        from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
        import matplotlib.patheffects as path_effects

        img_h, img_w = self._image_data.shape[:2]

        for ann in self.annotations:
            ann_type = ann.get('type', 'text')
            x = ann.get('x', 0)
            y = ann.get('y', 0)
            color = ann.get('color', 'white')
            relative = ann.get('relative', True)
            fontsize = ann.get('fontsize', 10)

            # Convert relative to absolute coordinates
            if relative:
                x = x * img_w
                y = y * img_h

            # Adjust y for matplotlib coordinate system
            if ann_type != 'text':
                y = img_h - y

            if ann_type == 'text':
                text = ann.get('text', '')
                ha = ann.get('ha', 'center')
                va = ann.get('va', 'center')
                fontweight = ann.get('fontweight', 'normal')

                # Create text with outline for better visibility
                txt = ax.text(
                    x, img_h - y, text,
                    color=color, fontsize=fontsize,
                    ha=ha, va=va, fontweight=fontweight
                )
                # Add outline effect
                txt.set_path_effects([
                    path_effects.withStroke(linewidth=2, foreground='black')
                ])

            elif ann_type == 'arrow':
                dx, dy = ann.get('arrow_direction', (0.1, 0))
                arrow_length = ann.get('arrow_length', 50)
                arrow_width = ann.get('arrow_width', 0.01)

                if relative:
                    dx = dx * img_w
                    dy = dy * img_h

                ax.annotate(
                    '', xy=(x + dx, y - dy), xytext=(x, y),
                    arrowprops=dict(
                        arrowstyle='->', color=color,
                        lw=ann.get('linewidth', 2),
                        mutation_scale=ann.get('head_size', 15)
                    )
                )

            elif ann_type == 'circle':
                size = ann.get('size', 10)
                circle = Circle(
                    (x, y), size,
                    facecolor='none', edgecolor=color,
                    linewidth=ann.get('linewidth', 2)
                )
                ax.add_patch(circle)

            elif ann_type == 'point':
                size = ann.get('size', 50)
                marker = ann.get('marker', 'o')
                ax.scatter(
                    [x], [y],
                    s=size, c=color, marker=marker,
                    edgecolors='black', linewidths=1
                )

            elif ann_type == 'line':
                x2 = ann.get('x2', x + 50)
                y2 = ann.get('y2', y)
                if relative:
                    x2 = x2 * img_w
                    y2 = y2 * img_h

                ax.plot(
                    [x, x2], [y, img_h - y2],
                    color=color, linewidth=ann.get('linewidth', 2),
                    linestyle=ann.get('linestyle', '-')
                )

            elif ann_type == 'rectangle':
                width = ann.get('width', 50)
                height = ann.get('height', 50)
                if relative:
                    width = width * img_w
                    height = height * img_h

                rect = Rectangle(
                    (x, y - height), width, height,
                    facecolor='none', edgecolor=color,
                    linewidth=ann.get('linewidth', 2),
                    linestyle=ann.get('linestyle', '--')
                )
                ax.add_patch(rect)

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
        """Validate panel configuration."""
        errors = []

        if not self.path.exists():
            errors.append(f"Image file not found: {self.path}")

        if self.crop is not None:
            if len(self.crop) != 4:
                errors.append("crop must be a 4-tuple (left, top, right, bottom)")
            elif any(v < 0 or v > 1 for v in self.crop):
                errors.append("crop values must be in [0, 1]")
            elif self.crop[0] >= self.crop[2] or self.crop[1] >= self.crop[3]:
                errors.append("crop: left < right and top < bottom required")

        if self.rotation not in self.VALID_ROTATIONS:
            errors.append(f"rotation must be one of {self.VALID_ROTATIONS}")

        if self.colormap is not None:
            try:
                import matplotlib.pyplot as plt
                plt.get_cmap(self.colormap)
            except ValueError:
                errors.append(f"Invalid colormap: {self.colormap}")

        if self.channel is not None:
            if isinstance(self.channel, str):
                if self.channel.lower() not in self.CHANNEL_NAMES:
                    errors.append(f"Invalid channel name: {self.channel}")

        if self.scale_bar_style not in ('bar', 'line'):
            errors.append("scale_bar_style must be 'bar' or 'line'")

        if not (0 <= self.scale_bar_bg_alpha <= 1):
            errors.append("scale_bar_bg_alpha must be in [0, 1]")

        if not (0 <= self.auto_contrast_cutoff[0] < self.auto_contrast_cutoff[1] <= 100):
            errors.append("auto_contrast_cutoff must be (low, high) with 0 <= low < high <= 100")

        return errors

    def __repr__(self) -> str:
        return f"ImagePanel('{self.path.name}')"
