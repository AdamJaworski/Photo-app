from PIL import Image
import cv2
from . import public_resources
from .HistoryLog import HistoryLog
import time
from numba import njit, prange
import numpy


@njit(fastmath=True)
def get_save_image_cv2(images, vis, base_image, index_):
    alpha_divisor = 255.0  # Move constant division out of the loop
    # Blending the images
    for index in prange(index_ + 1, len(images)):  # Start from the next image
        if not vis[index]:
            continue
        overlay_image = images[index]
        alpha_mask = overlay_image[:, :, 3] / alpha_divisor
        overlay = overlay_image[:, :, :3]
        background_mask = 1.0 - alpha_mask
        # Blend images
        for c in range(3):
            base_image[:, :, c] = (alpha_mask * overlay[:, :, c] + background_mask * base_image[:, :, c])

    return base_image


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
        self.update_display_size()
        self.layers = [[image_cv2, True]]
        self.active_layer = 0
        """"index of an active layer"""
        self.image_operations_history = [HistoryLog(self.layers[self.active_layer][0], "Open", self.active_layer)]
        self.images = [layer[0] for layer in self.layers]
        self.vis = [True]
        self.last_save = None
        self.save_name = None
        self.use_cv2_display_methode = False

    def benchmark_methode(self):
        self.use_cv2_display_methode = True

        time_for_cv2 = 0
        for i in range(10):
            start = time.time()
            self.get_display_image_cv2(self.images[0], 0)
            end = time.time()
            time_for_cv2 += (end - start)
        time_for_cv2 = time_for_cv2 / 10

        time_for_pillow = 0
        for i in range(10):
            start = time.time()
            self.get_display_image_pillow(self.images[0], 0)
            end = time.time()
            time_for_pillow += (end - start)
        time_for_pillow = time_for_pillow / 10

        print(f"CV2: {time_for_cv2.__round__(4)}s / PILLOW: {time_for_pillow.__round__(4)}s")
        self.use_cv2_display_methode = False if time_for_pillow < time_for_cv2 else True

    def get_display_image(self) -> Image:
        for index, vis_ in enumerate(self.vis):
            if vis_:
                break
        if not self.vis[index]:
            self.image_PIL = None
            return self.image_PIL
        # TODO pillow methode works great but doesn't display alpha mask
        # TODO cv2 just shows the base image - doesn't work at all
        if self.use_cv2_display_methode:
            self.image_PIL = self.get_display_image_cv2(self.images[index], index)
        else:
            self.image_PIL = self.get_display_image_pillow(self.images[index], index)

        self.image_PIL = self.image_PIL.resize(self.display_image_size, public_resources.display_rescale_methode)
        return self.image_PIL

    def get_display_image_cv2(self, base_image, index):
        return Image.fromarray(cv2.cvtColor(numpy.array(get_save_image_cv2(self.images, self.vis, base_image, index), dtype=numpy.uint8), cv2.COLOR_BGRA2RGBA))

    def get_display_image_pillow(self, base_image, index):
        base_image = Image.fromarray(cv2.cvtColor(base_image, cv2.COLOR_BGRA2RGBA))
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
        self.layers.append([self.image_cv2_on_load, True])
        self.images = [layer[0] for layer in self.layers]
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
