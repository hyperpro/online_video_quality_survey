import numpy as np
import random
from baseline_one_batch_simulator import OneBatchSimulator
from baseline_multi_batch_simulator import MultiBatchSimulator
from our_simulator import OurSimulator
from events import VideoTopo
from typing import List, Set, Dict
import process_simulation_results as sim_res

def baseline_1(num_user: int, num_video_per_batch: int) -> tuple[int, int]:
    simulator = OneBatchSimulator(n_user_per_batch=num_user, n_video_per_batch=num_video_per_batch)
    simulator.run()
    # print("Baseline 1: time consumed {time_consumed}, total video cost {cost}".format(
    #     time_consumed=simulator.time_consumed, cost=simulator.total_videos))
    return simulator.time_consumed, simulator.total_videos


def baseline_2(num_user: List[int], num_video_per_batch: List[int]) -> tuple[int, int]:
    simulator = MultiBatchSimulator(n_user_per_batch=num_user, n_video_per_batch=num_video_per_batch)
    simulator.run()
    # print("Baseline 2: time consumed {time_consumed}, total video cost {cost}".format(
    #     time_consumed=simulator.time_consumed, cost=simulator.total_videos))
    return simulator.time_consumed, simulator.total_videos


def ours(video_dependency: Dict[int, Set[int]], video_id_map_needed: Dict[int, int]) -> tuple[int, int]:
    video_topo = VideoTopo(video_dependency=video_dependency, video_id_map_needed=video_id_map_needed)
    simulator = OurSimulator(max_user_num=60, n_video_per_batch=10000, video_topo=video_topo)
    simulator.run()
    # print("Our method: time consumed {time_consumed}, total video cost {cost}".format(
    #     time_consumed=simulator.time_consumed, cost=simulator.total_videos))
    return simulator.time_consumed, simulator.total_videos


def sys_main() -> None:
    b1_cost = []
    b2_cost = []
    ours_cost = []
    opt_cost = []

    b1_time = []
    b2_time = []
    our_time = []

    for _ in range(0, 16):
        video_dependency = {1: {6, 7, 8, 15, 16, 17}, 2: {6, 7, 8, 15, 16, 17}, 3: {9, 10, 11, 18, 19, 20}, 4: {9, 10, 11, 18, 19, 20}, 5: {12, 13, 14, 21, 22, 23}, 6: set(), 7: set(),
                            8: set(), 9: set(), 10: set(), 11: set(), 12: set(), 13: set(), 14: set(), 15: set(), 16: set(), 17: set(), 18: set(), 19: set(), 20: set(), 21: set(), 22: set(), 23: set()}
        video_id_map_needed = {}
        opt = 0
        for i in range(1, 24):
            video_id_map_needed[i] = random.randint(11, 30)
            opt += video_id_map_needed[i]

        # video_dependency = {1: {6, 7, 8, 9, 10, 11}, 2: {6, 7, 8, 9, 10, 11}, 6: set(), 7: set(),
        #                     8: set(), 9: set(), 10: set(), 11: set()}
        # video_id_map_needed = {}
        # opt = 0
        # for i in range(1, 12):
        #     if i in video_dependency:
        #         video_id_map_needed[i] = random.randint(11, 30)
        #         opt += video_id_map_needed[i]
        opt_cost.append(opt)

        time_consumed, total_videos = baseline_1(num_user=30, num_video_per_batch=41)
        # time_consumed, total_videos = baseline_1(num_user=30, num_video_per_batch=17)

        b1_cost.append(total_videos)
        b1_time.append(time_consumed)

        time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[5, 18])
        # time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[2, 6])

        b2_cost.append(total_videos)
        b2_time.append(time_consumed)

        time_consumed, total_videos = ours(video_dependency=video_dependency, video_id_map_needed=video_id_map_needed)
        ours_cost.append(total_videos)
        our_time.append(time_consumed)

    sim_res.draw_time_cost(b1=b1_time, b2=b2_time, our=our_time)
    sim_res.draw_video_cost(b1=b1_cost, b2=b2_cost, our=ours_cost, opt=opt_cost)


if __name__ == '__main__':
    print('Start experiments')
    sys_main()
