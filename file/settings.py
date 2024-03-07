import cv2
import customtkinter
import tkinter
from structures import public_resources

is_app_open = False
local_rescale_methode: cv2


def start_gui():
    global is_app_open
    global local_rescale_methode

    def __on_close():
        global is_app_open
        settings_window.destroy()
        is_app_open = False

    def __on_apply(*args) -> None:
        global local_rescale_methode
        public_resources.update_viewport_on_new_thread = viewport_render.get()
        public_resources.display_rescale_methode = local_rescale_methode
        try:
            limit = int(history_limit_var.get())
            public_resources.image_history_limit = limit
        except Exception:
            history_limit_var.set(str(public_resources.image_history_limit))

        local_rescale_methode = public_resources.display_rescale_methode
        method_name = None
        possible_names = ['INTER_NEAREST', 'INTER_CUBIC', 'INTER_LINEAR', 'INTER_LANCZOS4', 'INTER_BITS', 'INTER_MAX']
        for name, value in vars(cv2).items():
            if value == local_rescale_methode:
                if possible_names.__contains__(name):
                    method_name = name
                    break
        scale_methode.set(method_name)
        viewport_render.select() if public_resources.update_viewport_on_new_thread else viewport_render.deselect()
        history_limit_var.set(str(public_resources.image_history_limit))

    @public_resources.refresh_viewport
    def __change_scaling_methode(choice) -> None:
        global local_rescale_methode
        match choice:
            case "CUBIC":
                local_rescale_methode = cv2.INTER_CUBIC
            case "LINEAR":
                local_rescale_methode = cv2.INTER_LINEAR
            case "NEAREST":
                local_rescale_methode = cv2.INTER_NEAREST
            case "LANCZOS":
                local_rescale_methode = cv2.INTER_LANCZOS4
            case "BITS":
                local_rescale_methode = cv2.INTER_BITS
            case "MAX":
                local_rescale_methode = cv2.INTER_MAX
            case _:
                raise UserWarning

    if is_app_open:
        return

    settings_window = customtkinter.CTkToplevel()
    settings_window.geometry("380x230+0+0")
    settings_window.title("Import image")
    settings_window.attributes('-topmost', True)
    settings_window.protocol("WM_DELETE_WINDOW", __on_close)

    customtkinter.CTkLabel(settings_window, text="Performance: ").pack()
    viewport_render = customtkinter.CTkCheckBox(settings_window, text="Render viewport on a new thread", height=25)
    viewport_render.pack()
    scale_methode_frame = customtkinter.CTkFrame(settings_window, height=25)
    scale_methode_frame.pack(side="top", fill='x', pady=5)
    customtkinter.CTkLabel(scale_methode_frame, text="Viewport scaling methode: ").pack(side="left", padx=5)
    scale_methode = customtkinter.CTkOptionMenu(scale_methode_frame,
                                                values=["CUBIC", "BITS", "LINEAR", "NEAREST", "LANCZOS", "MAX"],
                                                command=__change_scaling_methode, hover=True)
    history_limit_frame = customtkinter.CTkFrame(settings_window, height=25)
    history_limit_frame.pack(side="top", fill='x', pady=5)
    customtkinter.CTkLabel(history_limit_frame, text="History size limit: ").pack(side="left", padx=5)
    history_limit_var = tkinter.StringVar()
    history_limit_var.set(str(public_resources.image_history_limit))
    customtkinter.CTkEntry(history_limit_frame, textvariable=history_limit_var).pack(side="right")
    customtkinter.CTkButton(settings_window, text="Apply", command=__on_apply).pack()
    customtkinter.CTkButton(settings_window, text="Cancel", command=__on_close).pack(pady=5)

    viewport_render.select() if public_resources.update_viewport_on_new_thread else viewport_render.deselect()

    local_rescale_methode = public_resources.display_rescale_methode
    method_name = None
    possible_names = ['INTER_NEAREST', 'INTER_CUBIC', 'INTER_LINEAR', 'INTER_LANCZOS4', 'INTER_BITS', 'INTER_MAX']
    for name, value in vars(cv2).items():
        if value == local_rescale_methode:
            if possible_names.__contains__(name):
                method_name = name
                break
    scale_methode.set(method_name)
    scale_methode.pack(side="right")

    is_app_open = True
