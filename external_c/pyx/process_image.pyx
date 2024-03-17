# cython: language_level=3

import numpy as np
cimport numpy as cnp
import cv2  

def blend_images(cnp.ndarray dummy_alpha, list layers, cnp.ndarray input):
    cdef cnp.ndarray output = np.copy(input)    # This is over 50% time on 1 layer
    cdef cnp.ndarray alpha
    cdef cnp.ndarray image
    cdef bint visibility

    for image, visibility in layers:
        if not visibility:
            continue

        alpha = output[:, :, 3]

        if (alpha == dummy_alpha).all():
            return output.astype('uint8')

        alpha = cv2.merge([alpha, alpha, alpha, alpha])
        alpha /= 255.0

        output *= alpha
        image  *= (1.0 - alpha)
        output += image

    return np.clip(output, 0, 255).astype('uint8')

def clip_image(cnp.ndarray input):
    return np.clip(input, 0, 255).astype('uint8')