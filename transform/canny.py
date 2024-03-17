import gc
import customtkinter
import cv2
from structures import public_resources


@public_resources.image_operation
def start_gui():
    global image_copy, image_copy_
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]
    image_copy_ = cv2.cvtColor(image_copy, cv2.COLOR_RGBA2GRAY)
    image_copy_ = cv2.GaussianBlur(image_copy_, ksize=(3, 5), sigmaX=0.5)
    image_copy_ = image_copy.astype('uint8')

    def __on_close():
        global image_copy,image_copy_
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False
        image_copy, image_copy_ = None, None
        gc.collect()

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    @public_resources.refresh_viewport
    def __on_value_change(event=None):
        if not preview.get():
            return
        output = cv2.Canny(image_copy_, threshold1.get(), threshold2.get())
        public_resources.current_image_class.layers[
            public_resources.current_image_class.active_layer][0] = cv2.cvtColor(output, cv2.COLOR_GRAY2RGBA) # .astype('float32')
        output = None

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0].astype('float32')
        __on_close()
        return "Canny"

    @public_resources.refresh_viewport
    def __on_preview_change():
        if preview.get():
            __on_value_change()
        else:
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width - 340}+10")
    settings_window.title("Canny")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_cancel)

    threshold2 = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=255, command=__on_value_change)
    threshold1 = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=0, to=255, command=__on_value_change)
    threshold2.pack()
    threshold1.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True
