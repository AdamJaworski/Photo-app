import numpy as np
from structures import public_resources
import cv2
import customtkinter


@public_resources.image_operation
def start_gui():
    image_copy = public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0]
    # Convert BGR to BGRA (add an alpha channel)
    if image_copy.shape[2] == 3:
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2BGRA)

    def __on_close():
        settings_window.destroy()
        public_resources.is_image_operation_window_open = False

    @public_resources.refresh_viewport
    def __on_cancel():
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy
        __on_close()

    @public_resources.refresh_viewport
    def __on_value_change(event=None):
        if not preview.get():
            return

        # Replace with actual values from your color selection sliders or inputs
        lower_color = np.array([EXAMPLE_SLIDER.get(), 0, 0])  # Example: lower bound of color range
        upper_color = np.array([255, EXAMPLE_SLIDER_2.get(), EXAMPLE_SLIDER_2.get()])  # Example: upper bound of color range

        mask = cv2.inRange(cv2.cvtColor(image_copy, cv2.COLOR_BGRA2BGR), lower_color, upper_color)
        mask_rgba = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGBA)
        mask_inv = cv2.bitwise_not(mask_rgba)
        output = cv2.bitwise_and(image_copy, mask_inv)
        output[:, :, 3] = np.where(mask==255, 0, 255)
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = output
        output = None

    @public_resources.refresh_viewport
    @public_resources.save_state
    def __on_apply():
        preview.select(1)
        __on_value_change()
        __on_close()
        return "Color Range Cut"

    @public_resources.refresh_viewport
    def __on_preview_change():
        if preview.get():
            __on_value_change()
        else:
            public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = image_copy

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x180+{public_resources.screen_width - 340}+10")
    settings_window.title("Color Range Selection")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_cancel)

    # Adjust these sliders to control the lower and upper color range
    EXAMPLE_SLIDER = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=5, to=250, command=__on_value_change)
    EXAMPLE_SLIDER_2 = customtkinter.CTkSlider(settings_window, width=350, height=20, from_=5, to=250, command=__on_value_change)
    EXAMPLE_SLIDER.pack()
    EXAMPLE_SLIDER_2.pack()

    customtkinter.CTkButton(settings_window, text="Apply", command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_cancel).pack()

    preview = customtkinter.CTkCheckBox(settings_window, text="Preview", height=25, command=__on_preview_change)
    preview.select(1)
    preview.pack()
    __on_value_change()
    public_resources.is_image_operation_window_open = True
