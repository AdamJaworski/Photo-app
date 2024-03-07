import gc
import sys
import warnings
import psutil
from PIL import ImageTk
import customtkinter
import threading
from functools import partial
import cv2
import os

from experimental import blend_layers, cut
from file import open_image, save_image, settings
from transform import canny, vignette, blur
from color import hsv, rgb, brightness_contrast, brightness_contrast_alpha_beta
from structures import public_resources
from image import image_history, layers, resize
from structures.ImageClass import ImageClass


def __on_exit():
    app.destroy()
    sys.exit(1)


def __on_window_resize(event):
    if str(event.widget) != ".":
        return
    if public_resources.current_image_class is None:
        return
    public_resources.current_width_multiplier = event.width / 920
    old_size_active = public_resources.current_image_class.display_image_size
    for image_ in open_images_list:
        image_.update_display_size()
    if public_resources.current_image_class.display_image_size != old_size_active:
        __update_image(public_resources.current_image_class)


def __on_image_load(image_to_load):
    open_images_list.append(ImageClass(image_to_load))
    button_command = partial(__set_image_active, open_images_list[len(open_images_list) -1])
    customtkinter.CTkButton(button_frame, command=button_command, text=f"Image {len(open_images_list)}").pack(side="left", padx=3)
    __set_image_active(open_images_list[len(open_images_list) -1])


def __set_image_active(image_: ImageClass):
    if not public_resources.is_image_operation_window_open:
        if image_ != public_resources.current_image_class or public_resources.current_image_class is None:
            public_resources.current_image_class = image_
            __update_image(image_)
            public_resources.force_history_refresh()
            public_resources.force_layers_refresh()
    image_ = None


def __update_image(image_: ImageClass):
    if image_ is None:
        return
    image_.get_display_image_as_pillow()
    current_image_label.configure(image=(ImageTk.PhotoImage(image_.image_PIL) if image_.image_PIL is not None else image_.image_PIL))


def __refresh_image_buttons():
    for button in button_frame.winfo_children():
        button.destroy()
    for index, image_class in enumerate(open_images_list):
        text_ = f"Image {index + 1}" if image_class.save_name is None else image_class.save_name
        button_command = partial(__set_image_active, image_class)
        customtkinter.CTkButton(button_frame, command=button_command, text=text_).pack(side="left", padx=3)
        text_ = None
        button_command = None


def __clear_memory_on_close():
    open_images_list.remove(public_resources.current_image_class)
    for log in public_resources.current_image_class.image_operations_history:
        log.image = None
        log.operation_name = None
    self = public_resources.current_image_class
    self.layers = None
    self.image_cv2_on_load = None
    self.image_ratio = None
    self.image_ratio_ = None
    self.display_image_size = None
    self.default_image_size = None
    self.image_operations_history = None
    self.layers = None
    self.last_save = None
    self.image_PIL = None
    self = None
    public_resources.current_image_class = None
    gc.collect()


def close():
    if public_resources.current_image_class is None or public_resources.is_image_operation_window_open:
        return

    __clear_memory_on_close()

    if len(open_images_list) > 0:
        __set_image_active(open_images_list[0])
    else:
        global current_image_label
        public_resources.current_image_class = None
        public_resources.close_image_history()
        public_resources.close_layers()
        current_image_label.configure(image=None)

    __refresh_image_buttons()


def save():
    if public_resources.current_image_class is None:
        return
    if public_resources.current_image_class.last_save is None:
        save_image.start_gui()
    else:
        cv2.imwrite(public_resources.current_image_class.last_save, public_resources.current_image_class.get_save_image_cv2())


def transform_menu(choice):
    transform.set("Transform")
    match choice:
        case "Blur":
            blur.start_gui()
        case "Canny":
            canny.start_gui()
        case "Vignette":
            vignette.start_gui()
        case _:
            raise UserWarning("Not implemented choice")


def color_menu(choice):
    color.set("Color")
    match choice:
        case "HSV":
            hsv.start_gui()
        case "RGB":
            rgb.start_gui()
        case "Brightness/Contrast":
            brightness_contrast.start_gui()
        case "Brightness/Contrast OLD":
            brightness_contrast_alpha_beta.start_gui()
        case _:
            raise UserWarning("Not implemented choice")


def file_menu(choice):
    file.set("File")
    match choice:
        case "Open":
            if not public_resources.is_image_operation_window_open:
                open_image.start_gui()
        case "Save":
            save()
        case "Save as..":
            save_image.start_gui()
        case "Close":
            close()
        case "Settings":
            settings.start_gui()
        case "Debug":
            check()
        case "Test":
            pass
            #ram_test()
        case _:
            raise UserWarning("Not implemented choice")


def new_menu(choice):
    new.set("New")
    match choice:
        case "Blend layers":
            blend_layers.start_gui()
        case "Cut":
            cut.start_gui()
        case _:
            raise UserWarning("Not implemented choice")


def image_menu(choice):
    image.set("Image")
    match choice:
        case "Resize":
            resize.start_gui()
        case "History":
            image_history.start_gui()
        case "Layers":
            layers.start_gui()
        case _:
            raise UserWarning("Not implemented choice")


def check():
    os.system('cls')
    print("-"*20)
    # print(f"Number of open images: {len(open_images_list)}")
    print(f"Number of active threads: {threading.active_count()}")
    print(f"Update viewport on new thread: {True if public_resources.update_viewport_on_new_thread else False}")
    print(f"Limit of history logs: {public_resources.image_history_limit}")
    print(f"RAM used: {psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2:.2f} MB")
    if public_resources.current_image_class is not None:
        public_resources.current_image_class.benchmark_methode()
    print("-" * 20)


public_resources.current_image_class = None
# Frame
app = customtkinter.CTk()
app.title("Project Alpha")
app.bind("<Configure>", __on_window_resize)
app.protocol("WM_DELETE_WINDOW", __on_exit)

# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

#
main_buttons_frame = customtkinter.CTkFrame(app, height=128)
main_buttons_frame.pack(fill='x')


file = customtkinter.CTkOptionMenu(main_buttons_frame, values=["Open", "Save", "Save as..", "Close","Settings", "Debug", "Test"], command=file_menu, hover=True)
file.set("File")
file.pack(side="left")

image = customtkinter.CTkOptionMenu(main_buttons_frame, values=["Resize", "History", "Layers"], command=image_menu, hover=True)
image.set("Image")
image.pack(side="left")

transform = customtkinter.CTkOptionMenu(main_buttons_frame, values=["Blur", "Canny", "Vignette"], command=transform_menu, hover=True)
transform.set("Transform")
transform.pack(side="right")

color = customtkinter.CTkOptionMenu(main_buttons_frame, values=["HSV", "RGB", "Brightness/Contrast", "Brightness/Contrast OLD"], command=color_menu, hover=True)
color.set("Color")
color.pack(side="right")

new = customtkinter.CTkOptionMenu(main_buttons_frame, values=["Blend layers", "Cut"], command=new_menu, hover=True)
new.set("New")
new.pack(side="right")

#
button_frame = customtkinter.CTkFrame(app, height=32)
button_frame.pack(fill='x', pady=10)

current_image_label = customtkinter.CTkLabel(app, text="")
current_image_label.pack(pady=10)
open_images_list = []
button_list      = []

public_resources.do_viewport_update = __update_image
public_resources.on_image_load = __on_image_load
public_resources.image_buttons_refresh = __refresh_image_buttons
public_resources.screen_width = app.winfo_screenwidth()
public_resources.screen_height = app.winfo_screenheight()
center_x = int(public_resources.screen_width / 2 - 920 / 2)
center_y = int(public_resources.screen_height / 2 - 680 / 2)
app.geometry(f"920x680+{center_x}+{center_y}")
warnings.filterwarnings("ignore", message="CTkLabel Warning: Given image is not CTkImage but .* Image can not be scaled on HighDPI displays, use CTkImage instead.")
print(public_resources.display_rescale_methode)

app.mainloop()

