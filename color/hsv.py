import customtkinter
import cv2
from structures import public_resources
import numpy


@public_resources.image_operation
def start_gui():
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]
    image_copy_hsv = cv2.cvtColor( public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0], cv2.COLOR_RGB2HSV)
    global h, s, v, a
    h, s, v = cv2.split(image_copy_hsv)
    b, g, r, a = cv2.split(image_copy)

    def __on_close():
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    @public_resources.refresh_viewport
    def __on_value_change(event=None):
        global h, s, v, a
        if preview.get():
            h_ = numpy.multiply(h, slider_h.get())
            s_ = numpy.multiply(s, slider_s.get())
            v_ = numpy.multiply(v, slider_v.get())
            output_hvs = cv2.merge([h_, s_, v_])
            output_cv2 = cv2.cvtColor(output_hvs, cv2.COLOR_HSV2RGB)
            output_cv2 = cv2.merge((*cv2.split(output_cv2), a))
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = output_cv2

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        __on_close()
        return "HSV"

    @public_resources.refresh_viewport
    def __on_preview_change():
        if preview.get():
            __on_value_change()
        else:
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width - 340}+10")
    settings_window.title("HSV")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_cancel)

    slider_h = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=2, command=__on_value_change, number_of_steps=1000)
    slider_s = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=2, command=__on_value_change, number_of_steps=1000)
    slider_v = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=2, command=__on_value_change, number_of_steps=1000)

    slider_h.set(1), slider_s.set(1), slider_v.set(1)
    slider_h.pack()
    slider_s.pack()
    slider_v.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    public_resources.is_image_operation_window_open = True
    __on_value_change()

