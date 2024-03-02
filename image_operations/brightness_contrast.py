import customtkinter
import public_resources
import numpy


@public_resources.image_operation
def start_gui():
    image_copy = public_resources.current_image_class.image_cv2

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
            contrast_ = contrast.get()/2
            output_cv2 = image_copy.astype(numpy.float32)
            output_cv2 = numpy.power(output_cv2, contrast_)
            output_cv2 = numpy.add(output_cv2, brightness.get())
            output_cv2 = numpy.clip(output_cv2, 0, 255)
            public_resources.current_image_class.image_cv2 = output_cv2.astype(numpy.uint8)

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        __on_close()
        return "Brightness/Contrast"

    @public_resources.refresh_viewport
    def __on_preview_change():
        if preview.get():
            __on_value_change()
        else:
            public_resources.current_image_class.image_cv2 = image_copy

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width-340}+10")
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
