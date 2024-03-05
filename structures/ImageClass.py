import numpy as np
from PIL import Image
import cv2
from . import public_resources
from .HistoryLog import HistoryLog
import time
import numpy
from numba import jit, prange
from external_c.pyd import process_image


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
        self.use_cv2_display_methode = True

    def benchmark_methode(self):
        time_for_cv2 = 0
        for i in range(10):
            start = time.time()
            self.get_display_image_cv2(0)
            end = time.time()
            time_for_cv2 += (end - start)
        time_for_cv2 = time_for_cv2 / 10

        time_for_pillow = 0
        for i in range(10):
            start = time.time()
            self.get_display_image_pillow(0)
            end = time.time()
            time_for_pillow += (end - start)
        time_for_pillow = time_for_pillow / 10

        print(f"CV2: {time_for_cv2.__round__(4)}s / PILLOW: {time_for_pillow.__round__(4)}s")
        self.use_cv2_display_methode = False if time_for_pillow < time_for_cv2 else True

    def get_display_image(self) -> Image:

        for index, vis_ in enumerate(reversed(self.vis)):
            if vis_:
                break
        index = len(self.vis) - index - 1
        if not self.vis[index]:
            self.image_PIL = None
            return self.image_PIL

        # TODO pillow methode works great but doesn't display alpha mask
        if self.use_cv2_display_methode:
            self.image_PIL = self.get_display_image_cv2(index)
        else:
            self.image_PIL = self.get_display_image_pillow(index)
        start = time.time()
        self.image_PIL = self.image_PIL.resize(self.display_image_size, public_resources.display_rescale_methode)
        print(time.time() - start)
        return self.image_PIL

    def get_display_image_cv2(self, index):
        numba_list = self.layers[:index]
        numba_list.reverse()

        if len(numba_list) > 0:
            output = process_image.blend_images(self.dummy_alpha, numba_list, self.layers[index][0])
        else:
            output = self.layers[index][0].astype('uint8')

        return Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGRA2RGBA))

    def get_display_image_pillow(self, index):
        base_image = Image.fromarray(cv2.cvtColor(self.layers[index][0], cv2.COLOR_BGRA2RGBA))
        for layer in self.layers[index:]:
            if not layer[1]:
                continue
            overlay_image = Image.fromarray(cv2.cvtColor(layer[0], cv2.COLOR_BGRA2RGBA))
            r, g, b, alpha = overlay_image.split()
            base_image.paste(overlay_image, (0, 0), alpha)
        return base_image

    def update_display_size(self):
        self.display_image_size = (int(public_resources.current_width_multiplier * public_resources.default_image_width),
                                   int(public_resources.current_width_multiplier * public_resources.default_image_width * self.image_ratio))

    def create_new_layer(self) -> int:
        self.layers.append([self.image_cv2_on_load.astype('float32'), True])
        self.vis.append(True)
        return len(self.layers) - 1

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
