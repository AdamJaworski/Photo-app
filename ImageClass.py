from PIL import Image
from customtkinter import CTkImage
import cv2
from numpy import ndarray
import public_resources
from HistoryLog import HistoryLog


class ImageClass:
    image_cv2: ndarray
    image_cv2_on_load: ndarray
    image_PIL: Image
    image_CTk: CTkImage
    display_image_size: tuple
    default_image_size: tuple
    image_ratio: float
    image_ratio_: float
    image_operations_history: list

    def __init__(self, image_cv2):
        self.image_cv2 = image_cv2
        self.image_cv2_on_load = image_cv2
        self.image_ratio = image_cv2.shape[0] / image_cv2.shape[1]   # height / width
        self.image_ratio_ = image_cv2.shape[1] / image_cv2.shape[0]   # width / height
        self.display_image_size = (0, 0)
        self.default_image_size = (image_cv2.shape[1], image_cv2.shape[0])
        self.update_display_size()
        self.get_image_pil()
        self.image_operations_history = [HistoryLog(self.image_cv2, "Open")]
        self.layers = [self.image_cv2]
        self.last_save = None
        self.save_name = None

    def get_image_pil(self):
        self.image_PIL = Image.fromarray(cv2.cvtColor(self.image_cv2, cv2.COLOR_BGR2RGB))
        self.image_PIL = self.image_PIL.resize(self.display_image_size, public_resources.display_rescale_methode)
        return self.image_PIL

    def update_display_size(self):
        self.display_image_size = (int(public_resources.current_width_multiplier * public_resources.default_image_width),
                                   int(public_resources.current_width_multiplier * public_resources.default_image_width * self.image_ratio))

    def __del__(self):
        self.image_cv2 = None
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
