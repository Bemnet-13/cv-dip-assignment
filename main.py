import cv2
import matplotlib.pyplot as plt
import numpy as np


def plot_result(title, original, processed, is_gray=False):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    cmap = "gray" if is_gray else None

    axes[0].imshow(original, cmap=cmap)
    axes[0].set_title("Original")
    axes[0].axis("off")

    axes[1].imshow(processed, cmap=cmap)
    axes[1].set_title(title)
    axes[1].axis("off")

    plt.tight_layout()
    plt.show()


def load_image(path, as_gray=False):
    if as_gray:
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def image_negative(img):
    return 255 - img


def gamma_correction(img, gamma, c=1.0):
    img_normalized = img / 255.0
    corrected = c * np.power(img_normalized, gamma)
    return np.clip(corrected * 255, 0, 255).astype(np.uint8)


def logarithmic_transform(img):
    img_float = np.float32(img)
    c = 255.0 / np.log(1 + np.max(img_float))
    return np.uint8(c * np.log(1 + img_float))


def contrast_stretching(img):
    min_val = np.min(img)
    max_val = np.max(img)
    if max_val == min_val:
        return img
    stretched = (img - min_val) * (255.0 / (max_val - min_val))
    return np.clip(stretched, 0, 255).astype(np.uint8)


def histogram_equalization(img, is_gray=False):
    if is_gray:
        return cv2.equalizeHist(img)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)


def intensity_level_slicing(img, lower, upper, preserve_bg=True):
    sliced_img = np.copy(img)

    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        mask = (gray >= lower) & (gray <= upper)
        mask = mask[:, :, np.newaxis]
    else:
        mask = (img >= lower) & (img <= upper)

    if preserve_bg:
        sliced_img[np.broadcast_to(mask, img.shape)] = 255
    else:
        sliced_img = np.zeros_like(img)
        sliced_img[np.broadcast_to(mask, img.shape)] = 255

    return sliced_img


def bit_plane_slicing(img, bit_level):
    sliced = cv2.bitwise_and(img, 1 << bit_level)
    return np.uint8((sliced > 0) * 255)


def plot_all_bit_planes(img, title, is_gray=False):
    img_gray = img if is_gray else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    fig, axes = plt.subplots(2, 4, figsize=(15, 7))
    fig.suptitle(title, fontsize=16)
    axes = axes.flatten()

    for i in range(8):
        axes[i].imshow(bit_plane_slicing(img_gray, i), cmap="gray")
        if i == 0:
            label = f"Bit Plane {i} (LSB)"
        elif i == 7:
            label = f"Bit Plane {i} (MSB)"
        else:
            label = f"Bit Plane {i}"
        axes[i].set_title(label)
        axes[i].axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    img_rgb  = load_image("images/colorful_image_1.jpg", as_gray=False)
    img_gray = load_image("images/grayscale_image_1.jpg", as_gray=True)

    if img_rgb is None or img_gray is None:
        print("Error: image not found.")
    else:
        plot_result("Image Negative (RGB)",  img_rgb,  image_negative(img_rgb))
        plot_result("Image Negative (Gray)", img_gray, image_negative(img_gray), is_gray=True)

        plot_result("Gamma Correction γ=0.4 (RGB)",  img_rgb,  gamma_correction(img_rgb,  gamma=0.4))
        plot_result("Gamma Correction γ=2.2 (Gray)", img_gray, gamma_correction(img_gray, gamma=2.2), is_gray=True)

        plot_result("Logarithmic Transform (RGB)",  img_rgb,  logarithmic_transform(img_rgb))
        plot_result("Logarithmic Transform (Gray)", img_gray, logarithmic_transform(img_gray), is_gray=True)

        plot_result("Contrast Stretching (RGB)",  img_rgb,  contrast_stretching(img_rgb))
        plot_result("Contrast Stretching (Gray)", img_gray, contrast_stretching(img_gray), is_gray=True)

        plot_result("Histogram Equalization (RGB)",  img_rgb,  histogram_equalization(img_rgb))
        plot_result("Histogram Equalization (Gray)", img_gray, histogram_equalization(img_gray, is_gray=True), is_gray=True)

        sliced_rgb  = intensity_level_slicing(img_rgb,  lower=100, upper=150, preserve_bg=True)
        sliced_gray = intensity_level_slicing(img_gray, lower=100, upper=150, preserve_bg=False)
        plot_result("Intensity Slicing — Preserve BG (RGB)",  img_rgb,  sliced_rgb)
        plot_result("Intensity Slicing — Black BG (Gray)",    img_gray, sliced_gray, is_gray=True)

        plot_all_bit_planes(img_gray, "Bit Plane Slicing (Grayscale)", is_gray=True)
        plot_all_bit_planes(img_rgb,  "Bit Plane Slicing (RGB → Gray)")
