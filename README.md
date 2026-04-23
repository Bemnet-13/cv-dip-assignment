# Digital Image Processing — Elementary Methods

Individual assignment implementing seven fundamental intensity transformation methods in Python, handling both RGB and grayscale images.

## Methods Implemented

| # | Method | Formula |
|---|--------|---------|
| 1 | Image Negative | `s = 255 - r` |
| 2 | Gamma Correction | `s = c · r^γ` |
| 3 | Logarithmic Transform | `s = c · log(1 + r)` |
| 4 | Contrast Stretching | `s = (r - min) / (max - min) × 255` |
| 5 | Histogram Equalization | CDF-based redistribution |
| 6 | Intensity Level Slicing | Highlight pixels in range `[lower, upper]` |
| 7 | Bit Plane Slicing | Extract each of the 8 bit planes |

## Project Structure

```
.
├── main.py                    # All 7 transformations + visualization
├── images/
│   ├── colorful_image_1.jpg   # RGB input image
│   └── grayscale_image_1.jpg  # Grayscale input image
└── results/                   # Output figures saved by main.py
```

## Setup

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Usage

```bash
uv run python main.py
```

## Notes

- Histogram equalization for RGB operates on the Y channel in YCrCb space to avoid colour distortion.
- Intensity level slicing for RGB builds the mask from luminance so all three channels of a pixel are treated uniformly.
- Gamma and contrast stretching outputs are clipped to `[0, 255]` before casting to `uint8` to prevent overflow.
