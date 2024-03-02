import customtkinter
import cv2
import public_resources
import numpy


@public_resources.image_operation
def start_gui():
    image_copy = public_resources.current_image_class.image_cv2
    image_copy_rgb = cv2.cvtColor(public_resources.current_image_class.image_cv2, cv2.COLOR_BGR2RGB)

    def __on_close():
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.image_cv2 = image_copy
        __on_close()

    @public_resources.refresh_viewport
    def __on_value_change(event=None):
        if preview.get():
            (r, g, b) = cv2.split(image_copy_rgb)
            if multiply.get():
                r = numpy.clip(numpy.multiply(r.astype(numpy.float32), slider_r.get()).astype("uint8"), 0, 255)
                g = numpy.clip(numpy.multiply(g.astype(numpy.float32), slider_g.get()).astype("uint8"), 0, 255)
                b = numpy.clip(numpy.multiply(b.astype(numpy.float32), slider_b.get()).astype("uint8"), 0, 255)
            else:
                r = numpy.clip(numpy.add(r.astype(numpy.float32), (slider_r.get() - 1)*15).astype("uint8"), 0, 255)
                g = numpy.clip(numpy.add(g.astype(numpy.float32), (slider_g.get() - 1)*15).astype("uint8"), 0, 255)
                b = numpy.clip(numpy.add(b.astype(numpy.float32), (slider_b.get() - 1)*15).astype("uint8"), 0, 255)
            output_rgb = cv2.merge([r, g, b])
            output_cv2 = cv2.cvtColor(output_rgb, cv2.COLOR_RGB2BGR)
            public_resources.current_image_class.image_cv2 = output_cv2

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
            public_resources.current_image_class.image_cv2 = image_copy

    if public_resources.is_image_operation_window_open:
        return

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width-340}+10")
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
