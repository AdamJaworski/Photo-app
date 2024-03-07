import gc

import customtkinter
import cv2
from structures import public_resources
import numpy


@public_resources.image_operation
def start_gui():
    global b, g, r, a, image_copy
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]
    (r, g, b, a) = cv2.split(image_copy)

    def __on_close():
        global b, g, r, a, image_copy
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False
        b, g, r, a, image_copy = None, None, None, None, None
        gc.collect()

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    @public_resources.refresh_viewport
    # Works faster on single thread render
    def __on_value_change(event=None):
        global b, g, r, a
        if preview.get():
            if multiply.get():
                r_ = numpy.multiply(r, slider_r.get())
                g_ = numpy.multiply(g, slider_g.get())
                b_ = numpy.multiply(b, slider_b.get())
            else:
                r_ = numpy.add(r, (slider_r.get() - 1) * 15)
                g_ = numpy.add(g, (slider_g.get() - 1) * 15)
                b_ = numpy.add(b, (slider_b.get() - 1) * 15)
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = cv2.merge([r_, g_, b_, a])

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        __on_close()
        return "RGB"

    @public_resources.refresh_viewport
    def __on_preview_change():
        if preview.get():
            __on_value_change()
        else:
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy

    if public_resources.is_image_operation_window_open:
        return

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width - 340}+10")
    settings_window.title("RGB")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_cancel)

    slider_r = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=2, command=__on_value_change, number_of_steps=1000)
    slider_g = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=2, command=__on_value_change, number_of_steps=1000)
    slider_b = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=2, command=__on_value_change, number_of_steps=1000)

    slider_r.set(1), slider_g.set(1), slider_b.set(1)
    slider_r.pack()
    slider_g.pack()
    slider_b.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    multiply = customtkinter.CTkCheckBox(settings_window, text="Multiply", height=25, command=__on_preview_change)
    multiply.select(1)
    multiply.pack()
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True
