import random


def watch_each_video_time() -> int:
    # return 2000
    return random.randint(30000, 50000)


def watch_tutorial_time() -> int:
    # return 2000
    return random.randint(30000, 50000)


def time_delta_recruiting_i_th_worker(i: int = 0) -> int:
    # return 1000 * i
    # return random.randint(30000, 60000) * i
    return random.randint(5000, 15000) * i

def gap_between_batches() -> int:
    return 0


def print_perf_info(method: str, time_consumed: int, total_video_viewed: int) -> None:
    print("{method}: time consumed {time_consumed}, total video viewed {cost}".format(method=method,
                                                                                      time_consumed=time_consumed,
                                                                                      cost=total_video_viewed))
