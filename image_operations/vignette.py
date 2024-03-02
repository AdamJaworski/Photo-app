import customtkinter
import numpy as np
import public_resources
import numpy
import cv2


#test
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
            rows, cols = image_copy.shape[:2]
            kernel_x = cv2.getGaussianKernel(cols, int(x_val.get()))
            kernel_y = cv2.getGaussianKernel(rows, int(y_val.get()))
            kernel = (kernel_y * kernel_x.T)
            mask = 255 * kernel / np.linalg.norm(kernel)
            vignette = np.empty_like(image_copy)
            for i in range(3):
                vignette[:, :, i] = (image_copy[:, :, i] * mask).astype(np.uint8)
            public_resources.current_image_class.image_cv2 = vignette

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        __on_close()
        return "Vignette"

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

    x_val = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=100, to=512, command=__on_value_change)
    y_val  = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=100, to=512, command=__on_value_change)
    x_val.set(255)
    y_val.set(255)
    x_val.pack()
    y_val.pack()

    customtkinter.CTkButton(settings_window, text="Apply",  command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True
