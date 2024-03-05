import threading
import time
import cv2
import customtkinter
import tkinter
from structures import public_resources
import numpy as np


@public_resources.image_operation
def start_gui():
    def __on_close():
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False

    @public_resources.refresh_viewport
    def __on_apply():
        public_resources.current_image_class.default_image_size = (int(width.get()), int(height.get()))
        public_resources.current_image_class.dummy_alpha = np.full(fill_value=255, shape=(public_resources.current_image_class.default_image_size[1], public_resources.current_image_class.default_image_size[0])).astype('float32')

        for layer in public_resources.current_image_class.layers:
            layer[0] = cv2.resize(layer[0], public_resources.current_image_class.default_image_size, interpolation=resize_methode_)
            layer[0][:, :, 3] = np.clip(np.round(layer[0][:, :, 3]), 0, 255)
        public_resources.current_image_class.image_cv2_on_load = cv2.resize(public_resources.current_image_class.image_cv2_on_load, public_resources.current_image_class.default_image_size, interpolation=resize_methode_)
        __on_close()

    def __watchdog():
        current_width = int(width.get())
        current_height = int(height.get())
        while public_resources.is_image_operation_window_open:
            try:
                width_now = int(width.get())
                height_now = int(height.get())
            except Exception:
                width.set(str(current_width))
                width_now = int(width.get())
                height.set(str(current_height))
                height_now = int(width.get())

            if keep_scale.get():
                # on_height_change
                if current_height != height_now:
                    current_height = height_now
                    current_width = int(current_height * public_resources.current_image_class.image_ratio_)
                    width.set(str(current_width))
                # on_width_change
                elif current_width != width_now:
                    current_width = width_now
                    current_height = int(current_width * public_resources.current_image_class.image_ratio)
                    height.set(str(current_height))
            else:
                current_width  = width_now
                current_height = height_now
            time.sleep(0.1)

    def resize_methode_function(choice):
        global resize_methode_
        match choice:
            case "Cubic":
                resize_methode_ = cv2.INTER_CUBIC
            case "Nearest":
                resize_methode_ = cv2.INTER_NEAREST
            case "Linear":
                resize_methode_ = cv2.INTER_LINEAR
            case "Lanczos4":
                resize_methode_ = cv2.INTER_LANCZOS4

    if public_resources.is_image_operation_window_open:
        return

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry("320x200+0+0")
    settings_window.title("Resize")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_close)

    width = tkinter.StringVar()
    height = tkinter.StringVar()
    settings_frame = customtkinter.CTkFrame(settings_window, width=320, height=40, fg_color=settings_window.cget("fg_color"))
    settings_frame.pack(side="top", pady=10)
    customtkinter.CTkEntry(settings_frame, width=100, height=40, textvariable=width).pack(side="left", padx=30)
    customtkinter.CTkEntry(settings_frame, width=100, height=40, textvariable=height).pack(side="right", padx=30)
    width.set(public_resources.current_image_class.default_image_size[0])
    height.set(public_resources.current_image_class.default_image_size[1])
    resize_methode = customtkinter.CTkOptionMenu(settings_window, values=["Cubic", "Nearest",
                                                                          "Linear", "Lanczos4"],
                                                 hover=True, command=resize_methode_function)
    resize_methode_ = cv2.INTER_CUBIC
    resize_methode.set("Cubic")
    resize_methode.pack(pady=3)

    customtkinter.CTkButton(settings_window, text="Apply", command=__on_apply).pack(pady=3)
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_close).pack(pady=3)

    keep_scale = customtkinter.CTkCheckBox(settings_window, text="Keep scale", height=25)
    keep_scale.pack(pady=3)

    watchdog = threading.Thread(target=__watchdog)
    watchdog.start()
    public_resources.is_image_operation_window_open = True
