import cv2
import customtkinter
import tkinter
from structures import public_resources
from tkinter import filedialog


is_app_open = False


def start_gui():
    global is_app_open

    def __on_close():
        global is_app_open
        file_selector.destroy()
        is_app_open = False

    def __select_from_files():
        url_var.set(filedialog.askopenfilename())

    def __open():
        open_ = cv2.imread(url_var.get(), cv2.IMREAD_UNCHANGED)
        if open_ is not None:
            if open_.shape[2] == 3:
                open_ = cv2.cvtColor(open_, cv2.COLOR_BGR2BGRA)
            public_resources.on_image_load(open_)
            __on_close()
        del open_

    if is_app_open:
        return

    file_selector = customtkinter.CTkToplevel()
    file_selector.geometry("320x150+0+0")
    file_selector.title("Import image")
    file_selector.attributes('-topmost', True)
    file_selector.protocol("WM_DELETE_WINDOW", __on_close)

    url_var = tkinter.StringVar()
    customtkinter.CTkEntry(file_selector, width=350, height=40, textvariable=url_var).pack()

    customtkinter.CTkButton(file_selector, text="Open", command=__open).pack(pady=10)
    customtkinter.CTkButton(file_selector, text="Find", command=__select_from_files).pack()

    is_app_open = True
