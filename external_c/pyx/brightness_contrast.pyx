# cython: language_level=3
import numpy as np
cimport numpy as cnp

def change_image_contrast_and_brightness(cnp.ndarray[cnp.uint8_t, ndim=3] image, double contrast, double brightness):
    # Ensure inputs are in the correct format
    cdef cnp.ndarray[cnp.float64_t, ndim=3] float_image = image.astype(np.float64)

    # Apply contrast (power) and brightness adjustments
    float_image = np.power(float_image, contrast)
    float_image += brightness
    float_image = np.clip(float_image, 0, 255)

    # Convert back to an 8-bit format if necessary
    return float_image.astype(np.uint8)
