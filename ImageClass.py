import threading

import PIL
from PIL import Image
from customtkinter import CTkImage
import cv2
from numpy import ndarray
import public_resources
from HistoryLog import HistoryLog
import time

class ImageClass:
    image_cv2_on_load: ndarray
    image_PIL: Image
    image_CTk: CTkImage
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
        self.last_save = None
        self.save_name = None
        self.use_cv2_display_methode = True

    def benchmark_methode(self):
        self.use_cv2_display_methode = True

        time_for_cv2 = 0
        for i in range(10):
            start = time.time()
            self.get_display_image_cv2()
            end = time.time()
            time_for_cv2 += (end - start)
        time_for_cv2 = time_for_cv2 / 10

        time_for_pillow = 0
        for i in range(10):
            start = time.time()
            self.get_display_image_pillow()
            end = time.time()
            time_for_pillow += (end - start)
        time_for_pillow = time_for_pillow / 10

        print(f"CV2: {time_for_cv2.__round__(4)}s / PILLOW: {time_for_pillow.__round__(4)}s")

    def get_display_image(self) -> PIL.Image:
        if self.use_cv2_display_methode:
            self.image_PIL = self.get_display_image_cv2()
        else:
            self.image_PIL = self.get_display_image_pillow()
        self.image_PIL = self.image_PIL.resize(self.display_image_size, public_resources.display_rescale_methode)
        return self.image_PIL

    def get_save_image_cv2(self):
        base_image = self.layers[0][0]
        for layer in self.layers[1:]:
            if not layer[1]:
                continue
            overlay_image = layer[0]
            if overlay_image.shape[2] == 4:
                alpha_mask = overlay_image[:, :, 3] / 255.0
                overlay = overlay_image[:, :, :3]
                background_mask = 1.0 - alpha_mask
                for c in range(0, 3):
                    base_image[:, :, c] = (alpha_mask * overlay[:, :, c] + background_mask * base_image[:, :, c])
            else:
                base_image = overlay_image
        return base_image

    def get_display_image_cv2(self):
        return Image.fromarray(cv2.cvtColor(self.get_save_image_cv2(), cv2.COLOR_BGR2RGB))

    def get_display_image_pillow(self):
        base_image = Image.fromarray(cv2.cvtColor(self.layers[0][0], cv2.COLOR_BGR2RGB))
        for layer in self.layers[1:]:
            if not layer[1]:
                continue
            overlay_image = Image.fromarray(cv2.cvtColor(layer[0], cv2.COLOR_BGR2RGB))
            if overlay_image.mode == 'RGBA':
                r, g, b, alpha = overlay_image.split()
                base_image.paste(overlay_image, (0, 0), alpha)
            else:
                base_image.paste(overlay_image, (0, 0))
        return base_image

    def update_display_size(self):
        self.display_image_size = (int(public_resources.current_width_multiplier * public_resources.default_image_width),
                                   int(public_resources.current_width_multiplier * public_resources.default_image_width * self.image_ratio))

    def create_new_layer(self) -> int:
        self.layers.append([self.image_cv2_on_load, True])
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
