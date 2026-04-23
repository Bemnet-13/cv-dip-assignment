import cv2
import matplotlib.pyplot as plt
import numpy as np


# ==========================================
# HELPER FUNCTIONS FOR VISUALIZATION
# ==========================================
def plot_result(title, original, processed, is_gray=False):
    """Plots the original and processed image side-by-side."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    cmap = "gray" if is_gray else None

    axes[0].imshow(original, cmap=cmap)
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    axes[1].imshow(processed, cmap=cmap)
    axes[1].set_title(f"Processed: {title}")
    axes[1].axis("off")

    plt.tight_layout()
    plt.show()


def load_image(path, as_gray=False):
    """Loads an image and converts BGR to RGB for correct Matplotlib display."""
    if as_gray:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    else:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


# ==========================================
# 1. IMAGE NEGATIVE
# ==========================================
def image_negative(img):
    """Formula: s = 255 - r"""
    return 255 - img


# ==========================================
# 2. GAMMA ENCODING / CORRECTION
# ==========================================
def gamma_correction(img, gamma, c=1.0):
    """Formula: s = c * r^gamma"""
    img_normalized = img / 255.0
    corrected = c * np.power(img_normalized, gamma)
    return np.clip(corrected * 255, 0, 255).astype(np.uint8)


# ==========================================
# 3. LOGARITHMIC TRANSFORMATION
# ==========================================
def logarithmic_transform(img):
    """Formula: s = c * log(1 + r)"""
    # Convert to float to prevent overflow
    img_float = np.float32(img)
    # Calculate constant c to map max value to 255
    c = 255.0 / np.log(1 + np.max(img_float))

    # Apply log transform
    log_img = c * np.log(1 + img_float)
    return np.uint8(log_img)


# ==========================================
# 4. CONTRAST STRETCHING
# ==========================================
def contrast_stretching(img):
    """Formula: s = (r - min) / (max - min) * 255"""
    min_val = np.min(img)
    max_val = np.max(img)

    # Avoid division by zero in flat images
    if max_val == min_val:
        return img

    stretched = (img - min_val) * (255.0 / (max_val - min_val))
    return np.clip(stretched, 0, 255).astype(np.uint8)


# ==========================================
# 5. HISTOGRAM EQUALIZATION
# ==========================================
def histogram_equalization(img, is_gray=False):
    """
    Uses CDF to equalize histogram.
    RGB images are converted to YCrCb to equalize only the luminance channel.
    """
    if is_gray:
        return cv2.equalizeHist(img)
    else:
        # Convert RGB to YCrCb
        ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
        # Equalize the Y (Luminance) channel
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        # Convert back to RGB
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)


# ==========================================
# 6. INTENSITY LEVEL SLICING
# ==========================================
def intensity_level_slicing(img, lower, upper, preserve_bg=True):
    """Highlights intensities between lower and upper bounds."""
    sliced_img = np.copy(img)

    # For RGB, build mask from luminance so entire pixels are selected uniformly
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        mask2d = (gray >= lower) & (gray <= upper)
        mask = mask2d[:, :, np.newaxis]  # broadcast over 3 channels
    else:
        mask = (img >= lower) & (img <= upper)

    if preserve_bg:
        # Highlight specific range (make it white), preserve the rest
        sliced_img[np.broadcast_to(mask, img.shape)] = 255
    else:
        # Highlight specific range, make the rest black
        sliced_img = np.zeros_like(img)
        sliced_img[np.broadcast_to(mask, img.shape)] = 255

    return sliced_img


# ==========================================
# 7. BIT PLANE SLICING
# ==========================================
def bit_plane_slicing(img, bit_level):
    """Extracts a specific bit plane (0 to 7) using Bitwise AND."""
    # 1 << bit_level creates masks like 1, 2, 4, 8, 16, 32, 64, 128
    mask = 1 << bit_level
    sliced = cv2.bitwise_and(img, mask)
    # Scale to 255 so we can visualize it (0 becomes 0, >0 becomes 255)
    return np.uint8((sliced > 0) * 255)


def plot_all_bit_planes(img, title, is_gray=False):
    """Special plotting function to show all 8 bits in a single grid."""
    # Best visualized on a single channel. If RGB, convert to Gray for visualization.
    if not is_gray:
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img

    fig, axes = plt.subplots(2, 4, figsize=(15, 7))
    fig.suptitle(title, fontsize=16)
    axes = axes.flatten()

    for i in range(8):
        bit_img = bit_plane_slicing(img_gray, i)
        axes[i].imshow(bit_img, cmap="gray")
        axes[i].set_title(
            f"Bit Plane {i} (MSB)"
            if i == 7
            else (f"Bit Plane {i} (LSB)" if i == 0 else f"Bit Plane {i}")
        )
        axes[i].axis("off")

    plt.tight_layout()
    plt.show()


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Replace with the path to your actual images
    img_rgb = load_image("images/colorful_image_1.jpg", as_gray=False)
    img_gray = load_image("images/grayscale_image_1.jpg", as_gray=True)

    if img_rgb is not None and img_gray is not None:
        # --- 1. Image Negative ---
        plot_result(
            "1. Image Negative (RGB)", img_rgb, image_negative(img_rgb), is_gray=False
        )
        plot_result(
            "1. Image Negative (Gray)", img_gray, image_negative(img_gray), is_gray=True
        )

        # --- 2. Gamma Correction ---
        # Gamma < 1 brightens, Gamma > 1 darkens
        plot_result(
            "2. Gamma Correction (gamma=0.4)",
            img_rgb,
            gamma_correction(img_rgb, gamma=0.4),
            is_gray=False,
        )
        plot_result(
            "2. Gamma Correction (gamma=2.2)",
            img_gray,
            gamma_correction(img_gray, gamma=2.2),
            is_gray=True,
        )

        # --- 3. Logarithmic Transform ---
        plot_result(
            "3. Logarithmic Transform (RGB)",
            img_rgb,
            logarithmic_transform(img_rgb),
            is_gray=False,
        )
        plot_result(
            "3. Logarithmic Transform (Gray)",
            img_gray,
            logarithmic_transform(img_gray),
            is_gray=True,
        )

        # --- 4. Contrast Stretching ---
        plot_result(
            "4. Contrast Stretching (RGB)",
            img_rgb,
            contrast_stretching(img_rgb),
            is_gray=False,
        )
        plot_result(
            "4. Contrast Stretching (Gray)",
            img_gray,
            contrast_stretching(img_gray),
            is_gray=True,
        )

        # --- 5. Histogram Equalization ---
        plot_result(
            "5. Histogram Equalization (RGB)",
            img_rgb,
            histogram_equalization(img_rgb, is_gray=False),
            is_gray=False,
        )
        plot_result(
            "5. Histogram Equalization (Gray)",
            img_gray,
            histogram_equalization(img_gray, is_gray=True),
            is_gray=True,
        )

        # --- 6. Intensity Level Slicing ---
        # Slicing pixels with intensity between 100 and 150
        sliced_rgb = intensity_level_slicing(
            img_rgb, lower=100, upper=150, preserve_bg=True
        )
        sliced_gray = intensity_level_slicing(
            img_gray, lower=100, upper=150, preserve_bg=False
        )
        plot_result(
            "6. Intensity Slicing (Preserve BG)", img_rgb, sliced_rgb, is_gray=False
        )
        plot_result(
            "6. Intensity Slicing (Black BG)", img_gray, sliced_gray, is_gray=True
        )

        # --- 7. Bit Plane Slicing ---
        # Plotting all 8 planes in a grid
        plot_all_bit_planes(
            img_gray, "7. Bit Plane Slicing (Grayscale Image)", is_gray=True
        )
        plot_all_bit_planes(
            img_rgb, "7. Bit Plane Slicing (RGB converted to Gray)", is_gray=False
        )

    else:
        print("Error: One or both images not found! Please check the file paths.")
