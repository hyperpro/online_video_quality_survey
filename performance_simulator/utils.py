import random


def watch_each_video_time() -> int:
    # return 2000
    return random.randint(30000, 50000)

def watch_tutorial_time() -> int:
    # return 2000
    return random.randint(30000, 50000)


def time_delta_recruiting_i_th_worker(i: int = 0) -> int:
    # return 1000 * i
    return random.randint(30000, 60000) * i


def gap_between_batches() -> int:
    return 0
