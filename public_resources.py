import threading
from PIL.Image import BICUBIC
from HistoryLog import HistoryLog
from ImageClass import ImageClass
import time


def empty_function(*args):
    pass


update_viewport_on_new_thread = True
current_image_class: ImageClass
display_rescale_methode = BICUBIC
default_image_height = 600
default_image_width = 900
image_size = (900, 600)
current_width_multiplier = 1
screen_width = 0
screen_height = 0
image_history_limit = 20
is_image_operation_window_open = False
is_image_history_window_open   = False
is_save_image_window_open      = False
app_threads = []
# close_image_history_window = empty_function
# Public functions
force_history_refresh = empty_function
on_new_history_log    = empty_function
on_image_load         = empty_function
image_buttons_refresh = empty_function
do_viewport_update    = empty_function
close_image_history   = empty_function


def image_operation(func):
    def wrapper():
        if current_image_class is not None and not is_image_operation_window_open:
            func()
    return wrapper


def refresh_viewport(func):
    def wrapper(*args):
        update_thread = threading.Thread(target=do_viewport_update, args=(current_image_class,))
        func(*args)
        if update_viewport_on_new_thread:
            update_thread.start()
        else:
            do_viewport_update(current_image_class)
    return wrapper


def save_state(func):
    def wrapper():
        operation_name = func()
        new_log = HistoryLog(current_image_class.layers[current_image_class.active_layer][0], operation_name, current_image_class.layers[current_image_class.active_layer][1])
        current_image_class.image_operations_history.append(new_log)
        on_new_history_log(new_log)
    return wrapper


def measure_time(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        end = time.time()
        print(end - start)
    return wrapper