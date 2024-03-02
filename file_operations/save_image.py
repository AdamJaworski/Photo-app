import threading
import cv2
import customtkinter
import tkinter
import public_resources
from tkinter import filedialog
from os.path import isfile
extension = ".jpg"


@public_resources.image_operation
def start_gui():
    global extension

    def __on_close():
        global extension
        file_selector.destroy()
        public_resources.is_save_image_window_open = False
        extension = ".jpg"

    def __find_path():
        path.set(filedialog.askdirectory())

    def __save():
        global extension
        save_path = path.get() + "/" + name.get() + extension
        i = 0
        save_name = name.get()
        while isfile(save_path):
            save_path = path.get() + "/" + name.get() + str(i) + extension
            save_name = name.get() + str(i)
            i += 1
        print(save_path)
        cv2.imwrite(save_path, public_resources.current_image_class.image_cv2)
        public_resources.current_image_class.last_save = save_path
        public_resources.current_image_class.save_name = save_name
        threading.Thread(target=public_resources.image_buttons_refresh()).start()
        __on_close()

    def __select_extension(choice):
        global extension
        match choice:
            case ".jpg":
                extension = ".jpg"
            case ".png":
                extension = ".png"
            case ".tiff":
                extension = ".tiff"
            case ".bmp":
                extension = ".bmp"
            case _:
                raise UserWarning("Not implemented choice")

    if public_resources.is_save_image_window_open:
        return

    file_selector = customtkinter.CTkToplevel()
    file_selector.geometry("360x180+0+0")
    file_selector.title("Save")
    file_selector.attributes('-topmost', True)
    file_selector.protocol("WM_DELETE_WINDOW", __on_close)

    path_frame = customtkinter.CTkFrame(file_selector, width=320, height=30)
    path_frame.pack(side="top", pady=5)
    path = tkinter.StringVar()
    customtkinter.CTkEntry(path_frame, width=250, height=30, textvariable=path).pack(side="left", padx=5)
    customtkinter.CTkButton(path_frame, width=90, height=30, text="Find", command=__find_path).pack(side="right", padx=5)

    name_frame = customtkinter.CTkFrame(file_selector, width=320, height=30)
    name_frame.pack(side="top", pady=5)
    name = tkinter.StringVar()
    customtkinter.CTkEntry(name_frame, width=250, height=30, textvariable=name).pack(side="left", padx=5)
    extension_ = customtkinter.CTkOptionMenu(name_frame, width=90, height=30, values=[".jpg", ".png", ".tiff", ".bmp"], command=__select_extension)
    extension_.set(".jpg")
    extension = ".jpg"
    extension_.pack(side="right", padx=5)

    customtkinter.CTkButton(file_selector, text="Save", command=__save).pack()
    customtkinter.CTkButton(file_selector, text="Cancel", command=__on_close).pack(pady=5)

    public_resources.is_save_image_window_open = True
