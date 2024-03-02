import gc
import customtkinter
import HistoryLog
import public_resources


@public_resources.image_operation
def start_gui():
    def __on_close():
        public_resources.is_image_history_window_open = False
        public_resources.force_history_refresh = public_resources.empty_function
        public_resources.on_new_history_log    = public_resources.empty_function
        public_resources.close_image_history   = public_resources.empty_function
        settings_window.destroy()

    def __create_command(operation_log):
        return lambda : __on_recover(operation_log)

    @public_resources.refresh_viewport
    def __on_recover(operation_log: HistoryLog.HistoryLog):
        public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0] = operation_log.image
        if operation_log.operation_name == "Resize":
            public_resources.current_image_class.default_image_size = (public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0].shape[1],
                                                                       public_resources.current_image_class.layers[public_resources.current_image_class.active_layer][0].shape[0])
        operation_log = None

    def __on_new_log(__history_log):
        customtkinter.CTkButton(frame, text=__history_log.operation_name, command=__create_command(__history_log)).pack(fill='x', pady='2')
        if len(public_resources.current_image_class.image_operations_history) > public_resources.image_history_limit:
            __force_history_refresh()
        __history_log = None

    def __force_history_refresh():
        __assure_history_does_not_exceed_the_limit()
        for history_ in frame.winfo_children():
            history_.destroy()
        for __history_log in public_resources.current_image_class.image_operations_history:
            customtkinter.CTkButton(frame, text=__history_log.operation_name, command=__create_command(__history_log)).pack(fill='x', pady='2')

    def __assure_history_does_not_exceed_the_limit():
        while len(public_resources.current_image_class.image_operations_history) > public_resources.image_history_limit:
            public_resources.current_image_class.image_operations_history[0].image = None
            public_resources.current_image_class.image_operations_history[0].name  = None
            public_resources.current_image_class.image_operations_history.remove(public_resources.current_image_class.image_operations_history[0])
            gc.collect()

    if public_resources.is_image_history_window_open:
        return

    public_resources.force_history_refresh = __force_history_refresh
    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry(f"320x280+40+{public_resources.screen_height-340}")
    settings_window.title("ImageHistory")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_close)
    settings_window.resizable(False, False)

    frame = customtkinter.CTkScrollableFrame(settings_window, width=320, height=280)
    frame.pack()

    for __history_log in public_resources.current_image_class.image_operations_history:
        customtkinter.CTkButton(frame, text=__history_log.operation_name, command=__create_command(__history_log)).pack(fill='x', pady='2')

    public_resources.is_image_history_window_open = True
    public_resources.on_new_history_log  = __on_new_log
    public_resources.close_image_history = __on_close

