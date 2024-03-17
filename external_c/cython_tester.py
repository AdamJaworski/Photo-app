import time
from numba import jit

@jit
def sum_up_to_n(n):
    sum = 0
    for i in range(n + 1):
        sum += i
    return sum


if __name__ == "__main__":
    sum_up_to_n(1)
    n_ = 100000000
    start = time.time()
    py = sum_up_to_n(n_)
    end = time.time()
    from pyd.sum_numbers import sum_up_to_n
    c = sum_up_to_n(n_)
    end2 = time.time()

    print(f"Python:         {(end - start).__round__(4)}s\nExternal C:     {(end2 - end).__round__(4)}s")
    print(f"{py == c}")