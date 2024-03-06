import gc
import threading
import os
import psutil
import cv2
from .HistoryLog import HistoryLog
from .ImageClass import ImageClass
import time


def empty_function(*args):
    pass


update_viewport_on_new_thread = True
current_image_class: ImageClass
display_rescale_methode = cv2.INTER_CUBIC
default_image_height = 600
default_image_width = 900
image_size = (900, 600)
current_width_multiplier = 1
screen_width = 0
screen_height = 0
image_history_limit = 20
is_layer_window_open           = False
is_image_operation_window_open = False
is_image_history_window_open   = False
is_save_image_window_open      = False
app_threads = []
# close_image_history_window = empty_function
# Public functions
force_history_refresh = empty_function
force_layers_refresh  = empty_function
on_new_history_log    = empty_function
on_image_load         = empty_function
image_buttons_refresh = empty_function
do_viewport_update    = empty_function
close_image_history   = empty_function
close_layers          = empty_function


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
            if threading.active_count() > 8:
                return
            update_thread.start()
        else:
            #start = time.time()
            do_viewport_update(current_image_class)
            #print(f"Viewport update took: {(time.time() - start).__round__(4)}s to complete")
    return wrapper


def save_state(func):
    def wrapper():
        operation_name = func()
        new_log = HistoryLog(current_image_class.layers[current_image_class.active_layer][0], operation_name)
        current_image_class.image_operations_history.append(new_log)
        on_new_history_log(new_log)
        gc.collect()
    return wrapper


def measure_time(func):
    def wrapper(*args):
        start = time.time()
        output = func(*args)
        print(f"{(time.time() - start).__round__(4)}s")
        return output
    return wrapper


def ram_test(func, name: str, delay: float = 0.05):
    start_ram = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    print(f"Starting test for {name}...")
    for i in range(500):
        if int(i/100) == i/100:
            print(f"Finished {i}/500 refreshes current ram usage: {psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2:.2f} MB")
        func()
        time.sleep(delay)
    end_ram = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    print(f"Start {start_ram:.2f} MB, End {end_ram:.2f} MB")