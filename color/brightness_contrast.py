import gc
import os
import threading
import time
import customtkinter
from structures import public_resources
import numpy
from numba import njit
#from external_c.pyd import brightness_contrast

last_call = 0


@njit(fastmath=True, parallel=True)
def change_image_contrast_and_brightness(image, contrast: float, brightness: float):
    image_ = numpy.power(image, contrast)
    image_ = numpy.add(image_, brightness)
    return image_


@public_resources.image_operation
def start_gui():
    global image_copy
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]

    def __on_close():
        global image_copy
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False
        image_copy = None
        gc.collect()

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    def __on_value_change(event=None):
        global last_call
        if not preview.get():
            return
        if time.time() - last_call >= 0.06:
            threading.Thread(target=__update_image).start()
            last_call = time.time()

    @public_resources.refresh_viewport
    # Works faster on multithread render
    def __update_image():
        contrast_ = contrast.get() / 2
        brightness_ = brightness.get()
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = change_image_contrast_and_brightness(image_copy, contrast_, brightness_)

    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        time.sleep(0.1)
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0].astype('float32')
        __on_close()
        return "Brightness/Contrast"

    @public_resources.refresh_viewport
    def __on_preview_change():
        if preview.get():
            __on_value_change()
        else:
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width - 340}+10")
    settings_window.title("Brightness/Contrast")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_cancel)

    brightness = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=-128, to=128, command=__on_value_change)
    contrast  = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=1, to=3, command=__on_value_change, number_of_steps=1000)
    brightness.set(1)
    contrast.set(2)
    brightness.pack()
    contrast.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True

