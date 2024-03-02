import gc
import customtkinter
import HistoryLog
import public_resources


@public_resources.image_operation
def start_gui():
    def __on_close():
        public_resources.is_layer_window_open = False
        public_resources.force_layer_refresh  = public_resources.empty_function
        public_resources.close_layers         = public_resources.empty_function
        settings_window.destroy()

    def __create_command(layer_index):
        return lambda : __on_layer_change(layer_index)

    def __on_layer_change(layer_index: int):
        public_resources.current_image_class.active_layer = layer_index
        __force_layer_refresh()

    @public_resources.refresh_viewport
    def __delete_layer():
        if len(public_resources.current_image_class.layers) == 1:
            return
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = None
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][1] = None
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer] = None
        public_resources.current_image_class.layers.remove(public_resources.current_image_class.layers[public_resources.current_image_class.active_layer])
        public_resources.current_image_class.active_layer = 0
        __force_layer_refresh()
        gc.collect()

    def __create_new_layer():
        public_resources.current_image_class.create_new_layer()
        layer_index = len(public_resources.current_image_class.layers) - 1
        customtkinter.CTkButton(layer_buttons_frames, text=f"Layer {layer_index}", command=__create_command(layer_index)).pack(fill='x', pady='2')

    def __force_layer_refresh():
        for layers_ in layer_buttons_frames.winfo_children():
            layers_.destroy()
        button_list = []
        for i in range(len(public_resources.current_image_class.layers)):
            button_list.append(customtkinter.CTkButton(layer_buttons_frames, text=f"Layer {i}", command=__create_command(i)))
            button_list[len(button_list) - 1].pack(fill='x', pady='2')
        button_list[public_resources.current_image_class.active_layer].configure(fg_color="grey")

    if public_resources.is_layer_window_open:
        return

    public_resources.force_layer_refresh = __force_layer_refresh
    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x280+{public_resources.screen_width-400}+{public_resources.screen_height-540}")
    settings_window.title("Layers")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_close)
    control_buttons_frame = customtkinter.CTkFrame(settings_window, height=50)
    control_buttons_frame.pack(fill="x")

    customtkinter.CTkButton(control_buttons_frame, text=f"Create new layer", command=__create_new_layer).pack(side="left", padx='2')
    customtkinter.CTkButton(control_buttons_frame, text=f"Remove layer", command=__delete_layer).pack(side="right", padx='2')

    layer_buttons_frames = customtkinter.CTkScrollableFrame(settings_window)
    layer_buttons_frames.pack(fill="both", expand=True, pady=5)
    button_list = []
    for index, layer in enumerate(public_resources.current_image_class.layers):
        button_list.append(customtkinter.CTkButton(layer_buttons_frames, text=f"Layer {index}", command=__create_command(index)))
        button_list[len(button_list) -1].pack(fill='x', pady='2')

    button_list[public_resources.current_image_class.active_layer].configure(fg_color="grey")
    public_resources.is_layer_window_open = True
    public_resources.close_layers = __on_close
    public_resources.force_layers_refresh = __force_layer_refresh

