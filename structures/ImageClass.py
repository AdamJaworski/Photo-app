import numpy as np
from PIL import Image
import cv2
from . import public_resources
from .HistoryLog import HistoryLog
import time
import numpy
from numba import njit, prange
from external_c.pyd import process_image


@njit(fastmath=True)
def clip_image(image):
    # image_ = np.clip(image, 0, 255).astype('uint8')
    # return image_
    return image.astype('uint8')


def blend_images(dummy_alpha, layers, base_image):
    output = np.copy(base_image)
    for (image, visibility) in layers:
        if not visibility:
            continue

        alpha = output[:, :, 3]
        if (alpha == dummy_alpha).all():
            return output.astype('uint8')

        alpha = alpha.astype('float32') / 255.0
        alpha = cv2.merge([alpha, alpha, alpha, alpha])

        output *= alpha
        image  *= 1.0 - alpha
        output += image

    return numpy.clip(output, 0, 255).astype('uint8')


class ImageClass:
    image_PIL: Image
    display_image_size: tuple
    default_image_size: tuple
    image_ratio: float
    image_ratio_: float
    image_operations_history: list
    use_cv2_display_methode: bool

    def __init__(self, image_cv2):
        self.image_cv2_on_load = image_cv2
        self.image_ratio = image_cv2.shape[0] / image_cv2.shape[1]   # height / width
        self.image_ratio_ = image_cv2.shape[1] / image_cv2.shape[0]   # width / height
        self.display_image_size = (0, 0)
        self.default_image_size = (image_cv2.shape[1], image_cv2.shape[0])
        self.dummy_alpha = np.full(fill_value=255, shape=(self.default_image_size[1], self.default_image_size[0])).astype('float32')
        self.update_display_size()
        self.layers = [[image_cv2.astype('float32'), True]]
        self.active_layer = 0
        """"index of an active layer"""
        self.image_operations_history = [HistoryLog(self.layers[self.active_layer][0], "Open")]
        self.vis = [True]
        self.last_save = None
        self.save_name = None

    def benchmark_methode(self):
        self.rescale_with_cv()
        self.rescale_with_pillow()

    def get_display_image_as_pillow(self) -> Image:
        self.image_PIL = None
        for index, vis_ in enumerate(reversed(self.vis)):
            if vis_:
                break
        index = len(self.vis) - index - 1
        if not self.vis[index]:
            return self.image_PIL

        self.image_PIL = cv2.resize(self.get_display_image_cv2(index), self.display_image_size, interpolation=public_resources.display_rescale_methode)
        self.image_PIL = Image.fromarray(self.image_PIL)

        return self.image_PIL

    def get_display_image_cv2(self, index):
        numba_list = self.layers[:index]
        numba_list.reverse()

        if len(numba_list) > 0:
            return process_image.blend_images(self.dummy_alpha, numba_list, self.layers[index][0])
        else:
            return process_image.clip_image(self.layers[index][0])

    def get_save_image_cv2(self):
        for index, vis_ in enumerate(reversed(self.vis)):
            if vis_:
                break
        index = len(self.vis) - index - 1
        if not self.vis[index]:
            return None
        return self.get_display_image_cv2(index)

    def update_display_size(self):
        if public_resources.display_real_size:
            self.display_image_size = self.default_image_size * public_resources.zoom
        else:
            self.display_image_size = (int(public_resources.current_width_multiplier * public_resources.default_image_width),
                                       int(public_resources.current_width_multiplier * public_resources.default_image_width * self.image_ratio))

    def create_new_layer(self) -> int:
        self.layers.append([self.image_cv2_on_load.astype('float32'), True])
        self.vis.append(True)
        return len(self.layers) - 1

    def rescale_with_pillow(self):
        input_ = self.get_display_image_cv2(0)
        start = time.time()
        pil = Image.fromarray(input_)
        pil = pil.resize(self.display_image_size, Image.LANCZOS)
        print(f"Rescale with pillow: {(time.time() - start).__round__(4)}s")

    def rescale_with_cv(self):
        input_ = self.get_display_image_cv2(0)
        start = time.time()
        pil = cv2.resize(input_, self.display_image_size, interpolation=cv2.INTER_LANCZOS4)
        Image.fromarray(pil)
        print(f"Rescale with cv2: {(time.time() - start).__round__(4)}s")

    def __del__(self):
        self.active_layer = None
        self.image_cv2_on_load = None
        self.image_ratio = None
        self.image_ratio_ = None
        self.display_image_size = None
        self.default_image_size = None
        self.image_operations_history = None
        self.layers = None
        self.last_save = None
        self.save_name = None
        self.image_PIL = None