import gc
import customtkinter
from structures import public_resources

button_list = []
vis_button_list = []
frames = []


def start_gui():
    global button_list
    global vis_button_list
    global frames
    height_buttons = 30
    no_vis_fg_color = "#8B0000"
    default_color = "#1F6AA5"

    def __on_close():
        global button_list
        global vis_button_list
        global frames
        public_resources.is_layer_window_open = False
        public_resources.force_layers_refresh = public_resources.empty_function
        public_resources.close_layers         = public_resources.empty_function
        button_list = []
        vis_button_list = []
        frames = []
        settings_window.destroy()

    def __create_command(layer_index):
        return lambda : __on_layer_change(layer_index)

    def __create_command_vis(layer_index):
        return lambda : __change_visibility(layer_index)

    @public_resources.refresh_viewport
    def __change_visibility(layer_index: int):
        global button_list
        global vis_button_list
        global frames
        public_resources.current_image_class.layers[layer_index][1] = not public_resources.current_image_class.layers[layer_index][1]
        public_resources.current_image_class.vis[layer_index] = not public_resources.current_image_class.vis[layer_index]
        if public_resources.current_image_class.layers[layer_index][1]:
            button_list[layer_index].configure(fg_color=default_color)
            vis_button_list[layer_index].configure(fg_color=default_color)
        else:
            button_list[layer_index].configure(fg_color=no_vis_fg_color)
            vis_button_list[layer_index].configure(fg_color=no_vis_fg_color)
        button_list[public_resources.current_image_class.active_layer].configure(fg_color="grey")

    def __on_layer_change(layer_index: int):
        if public_resources.is_image_operation_window_open:
            return
        if layer_index == public_resources.current_image_class.active_layer:
            return
        global button_list
        global vis_button_list
        global frames
        previous_index = public_resources.current_image_class.active_layer
        public_resources.current_image_class.active_layer = layer_index

        button_list[public_resources.current_image_class.active_layer].configure(fg_color="grey")
        if previous_index <= len(public_resources.current_image_class.layers) - 1:
            button_list[previous_index].configure(fg_color=default_color) if public_resources.current_image_class.vis[previous_index] else button_list[previous_index].configure(fg_color=no_vis_fg_color)

    @public_resources.refresh_viewport
    def __delete_layer():
        global button_list
        global vis_button_list
        global frames
        if len(public_resources.current_image_class.layers) == 1:
            return
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = None
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][1] = None
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer] = None
        public_resources.current_image_class.layers.remove(None)

        public_resources.current_image_class.vis[public_resources.current_image_class.active_layer] = None
        public_resources.current_image_class.vis.remove(None)

        public_resources.current_image_class.active_layer = len(public_resources.current_image_class.layers) - 1
        __force_layer_refresh()
        gc.collect()

    @public_resources.refresh_viewport
    def __create_new_layer():
        global button_list
        global vis_button_list
        global frames
        public_resources.current_image_class.create_new_layer()
        layer_index = len(public_resources.current_image_class.layers) - 1
        frames.append(customtkinter.CTkFrame(layer_buttons_frames, height=height_buttons))
        frames[layer_index].pack(fill='x', pady='2')
        vis_button_list.append(customtkinter.CTkButton(frames[layer_index], text=f"V", width=40, height=height_buttons, command=__create_command_vis(layer_index)))
        vis_button_list[layer_index].pack(side="right")
        button_list.append(customtkinter.CTkButton(frames[layer_index], text=f"Layer {layer_index}", height=height_buttons, command=__create_command(layer_index)))
        button_list[layer_index].pack(fill='x', padx='2')

    def __force_layer_refresh():
        global button_list
        global vis_button_list
        global frames
        for layers_ in layer_buttons_frames.winfo_children():
            layers_.destroy()

        button_list = []
        frames = []
        vis_button_list = []

        for index, layer in enumerate(public_resources.current_image_class.layers):
            frames.append(customtkinter.CTkFrame(layer_buttons_frames, height=height_buttons))
            frames[index].pack(fill='x', pady='2')
            vis_button_list.append(customtkinter.CTkButton(frames[index], text=f"V", width=40, height=height_buttons, command=__create_command_vis(index)))
            vis_button_list[len(vis_button_list) - 1].pack(side="right")
            button_list.append(customtkinter.CTkButton(frames[index], text=f"Layer {index}", height=height_buttons, command=__create_command(index)))
            button_list[len(button_list) - 1].pack(fill='x', padx='2')
            if not layer[1]:
                button_list[index].configure(fg_color=no_vis_fg_color)
                vis_button_list[index].configure(fg_color=no_vis_fg_color)

        button_list[public_resources.current_image_class.active_layer].configure(fg_color="grey")

    if public_resources.is_layer_window_open:
        return

    public_resources.force_layer_refresh = __force_layer_refresh
    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x280+{public_resources.screen_width - 400}+{public_resources.screen_height - 540}")
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
    vis_button_list = []
    frames = []
    for index, layer in enumerate(public_resources.current_image_class.layers):
        frames.append(customtkinter.CTkFrame(layer_buttons_frames, height=height_buttons))
        frames[index].pack(fill='x', pady='2')
        vis_button_list.append(customtkinter.CTkButton(frames[index], text=f"V", width=40, height=height_buttons, command=__create_command_vis(index)))
        vis_button_list[len(vis_button_list) -1].pack(side="right")
        button_list.append(customtkinter.CTkButton(frames[index], text=f"Layer {index}", height=height_buttons, command=__create_command(index)))
        button_list[len(button_list) -1].pack(fill='x', padx='2')
        if not layer[1]:
            button_list[index].configure(fg_color=no_vis_fg_color)
            vis_button_list[index].configure(fg_color=no_vis_fg_color)

    button_list[public_resources.current_image_class.active_layer].configure(fg_color="grey")
    public_resources.is_layer_window_open = True
    public_resources.close_layers = __on_close
    public_resources.force_layers_refresh = __force_layer_refresh

