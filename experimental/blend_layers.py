import gc
import customtkinter
import cv2
from structures import public_resources


@public_resources.image_operation
def start_gui():
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]

    def __on_close():
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False
        gc.collect()

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    @public_resources.refresh_viewport
    def __on_value_change(event=None):
        if not preview.get():
            return
        public_resources.current_image_class.layers[
            public_resources.current_image_class.active_layer][0] = cv2.addWeighted(image_copy, alpha.get(), public_resources.current_image_class.layers[0][0], 1 - alpha.get(), 0)

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        __on_close()
        return "Blend layers"

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

    alpha = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=1, command=__on_value_change, number_of_steps=1000)
    alpha.set(0.5)
    alpha.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True
