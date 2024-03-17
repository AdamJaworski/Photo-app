import customtkinter
import cv2
from structures import public_resources


@public_resources.image_operation
def start_gui():
    global image_copy
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]
    alpha = image_copy[:, :, 3]

    def __on_close():
        global image_copy
        settings_window.destroy()
        image_copy = None
        public_resources.is_image_operation_window_open = False

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    @public_resources.refresh_viewport
    def __on_value_change(event=None):
        if not preview.get():
            return
        output_cv2 = cv2.bilateralFilter(cv2.cvtColor(image_copy, cv2.COLOR_RGBA2RGB), int(slider_d.get()), slider_strength.get(), slider_strength.get())
        output_cv2 = cv2.merge((*cv2.split(output_cv2), alpha))
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = output_cv2

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0].astype('float32')
        __on_close()
        return "Blur"

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
    settings_window.title("Blur")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_cancel)

    slider_d = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=1, to=10, command=__on_value_change)
    slider_strength = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=255,
                                              command=__on_value_change)

    slider_d.pack()
    slider_strength.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True
