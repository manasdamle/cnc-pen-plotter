import cv2
import numpy as np
import matplotlib.pyplot as plt


def convert_to_stencil(path, min_area=100, blur_size=5, block_size=11, C=3, kernel_size=2):
    """
    Converts an image to a clean black-and-white stencil-like outline.

    Parameters:
    - path: str, path to the input image
    - min_area: int, minimum pixel area for keeping a connected component (removes tiny specks)
    - blur_size: int, size of the Gaussian blur kernel (must be odd); higher = more blur = softer outlines
    - block_size: int, size of neighborhood for adaptive thresholding (must be odd); smaller = more sensitive to local contrast
    - C: int, constant subtracted from mean in adaptive thresholding; higher = darker output
    - kernel_size: int, size of morphological opening kernel; helps clean up small gaps and specks
    """

    # Load and convert image to grayscale
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to smooth out noise
    blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

    # Adaptive thresholding to get binary image
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size, C
    )

    # Morphological opening to remove small white noise
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Remove small specks by filtering connected components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
    filtered = np.zeros_like(cleaned)
    for i in range(1, num_labels):  # skip background
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            filtered[labels == i] = 255

    # Invert so that outlines are black on white
    inverted = cv2.bitwise_not(filtered)

    # Show final result
    plt.imshow(inverted, cmap='gray')
    plt.axis('off')
    plt.show()

    return inverted


# Example usage with adjustable parameters
if __name__ == "__main__":
    convert_to_stencil(
        "testphoto2.png",
        min_area=100,    # Higher = fewer small dots
        blur_size=3,     # 3, 5, or 7 typically — higher softens detail
        block_size=21,   # Must be odd; 9-15 works well for most images
        C=1,             # Tweaks threshold sensitivity; higher = more aggressive
        kernel_size=2    # 1 or 2 is usually enough
    )
