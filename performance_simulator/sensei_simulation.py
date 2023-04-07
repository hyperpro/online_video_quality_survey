import collections
import random

import numpy as np

from baseline_one_batch_simulator import OneBatchSimulator
from baseline_multi_batch_simulator import MultiBatchSimulator
from our_simulator import OurSimulator
from events import VideoTopo
from typing import List, Set, Dict
import process_simulation_results as sim_res
import utils


def baseline_1(num_user: int, num_video_per_batch: int) -> tuple[int, int]:
    simulator = OneBatchSimulator(n_user_per_batch=num_user, n_video_per_batch=num_video_per_batch)
    simulator.run()
    # utils.print_perf_info(method='Baseline 1', time_consumed=simulator.time_consumed,
    #                       total_video_viewed=simulator.total_videos)
    return simulator.time_consumed, simulator.total_videos


def baseline_2(num_user: List[int], num_video_per_batch: List[int]) -> tuple[int, int]:
    simulator = MultiBatchSimulator(n_user_per_batch=num_user, n_video_per_batch=num_video_per_batch)
    simulator.run()
    # utils.print_perf_info(method='Baseline 2', time_consumed=simulator.time_consumed,
    #                       total_video_viewed=simulator.total_videos)
    return simulator.time_consumed, simulator.total_videos


def ours(video_dependency: Dict[int, Set[int]], video_id_map_needed: Dict[int, int], max_num_videos: int,
         spend_scale: float, max_active_user: int = 60) -> tuple[int, int]:
    video_topo = VideoTopo(video_dependency=video_dependency, video_id_map_needed=video_id_map_needed)
    simulator = OurSimulator(max_num_videos=max_num_videos, cost_scale=spend_scale, video_topo=video_topo,
                             max_active_user=max_active_user)
    simulator.run()
    # utils.print_perf_info(method='Ours', time_consumed=simulator.time_consumed,
    #                       total_video_viewed=simulator.total_videos)
    return simulator.time_consumed, simulator.total_videos


def generate_tree(id_start: int, first_level_num: int, second_level_num: int, rating_low: int = 11) -> \
        tuple[Dict[int, Set[int]], Dict[int, int]]:
    rating_needed_low = rating_low
    rating_needed_high = 30
    video_dependency = collections.defaultdict(set)
    video_id_map_needed = {}
    for first_id in range(id_start, id_start + first_level_num):
        for second_id in range(id_start + first_level_num, id_start + first_level_num + second_level_num):
            video_dependency[first_id].add(second_id)

    for second_id in range(id_start + first_level_num, id_start + first_level_num + second_level_num):
        video_dependency[second_id] = set()

    for video_id in range(id_start, id_start + first_level_num + second_level_num):
        video_id_map_needed[video_id] = random.randint(rating_needed_low, rating_needed_high)

    return video_dependency, video_id_map_needed


def enumerate_trees() -> None:
    print('Perf with number of trees')
    opt_cost = []
    b1_cost = []
    b2_cost = []
    our_cost = []
    b1_time = []
    b2_time = []
    our_time = []

    for n_tree in range(1, 11):
        print('Processing tree {tree}'.format(tree=n_tree))
        b1_sess = []
        b2_sess = []
        our_sess = []
        opt_sess = []
        time_1 = []
        time_2 = []
        time_3 = []

        for _ in range(0, 16):
            video_dependency = {}
            video_id_map_needed = {}
            start_id = 0
            first_level_num = 4
            second_level_num = first_level_num * 4
            second_level_group = 3
            for tree_id in range(0, n_tree):
                this_video_dependency, this_video_id_map_needed = generate_tree(id_start=start_id,
                                                                                first_level_num=first_level_num,
                                                                                second_level_num=second_level_num)
                video_dependency.update(this_video_dependency)
                video_id_map_needed.update(this_video_id_map_needed)
                start_id += first_level_num + second_level_num

            # b1
            time_consumed, total_videos = baseline_1(num_user=30,
                                                     num_video_per_batch=(first_level_num +
                                                                          second_level_num * second_level_group) * n_tree)
            b1_sess.append(total_videos)
            time_1.append(time_consumed)

            # b2
            time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[first_level_num * n_tree,
                                                                                             second_level_num * n_tree])
            b2_sess.append(total_videos)
            time_2.append(time_consumed)

            # ours
            time_consumed, total_videos = ours(video_dependency=video_dependency,
                                               video_id_map_needed=video_id_map_needed, max_num_videos=50,
                                               spend_scale=0.6, max_active_user=60)
            our_sess.append(total_videos)
            time_3.append(time_consumed)

            opt_sess.append(sum(video_id_map_needed.values()))

        opt_cost.append(sum(opt_sess) / len(opt_sess))
        our_cost.append(sum(our_sess) / len(our_sess))
        b1_cost.append(sum(b1_sess) / len(b1_sess))
        b2_cost.append(sum(b2_sess) / len(b2_sess))

        b1_time.append(sum(time_1) / len(time_1))
        b2_time.append(sum(time_2) / len(time_2))
        our_time.append(sum(time_3) / len(time_3))

    x_axis = list(range(1, 11))
    sim_res.draw_sess_line(b1_x=x_axis, b1_y=b1_cost, b2_x=x_axis, b2_y=b2_cost, b3_x=x_axis, b3_y=our_cost,
                           b4_x=x_axis, b4_y=opt_cost, x_label="Number of trees", y_label="Number of sessions")
    sim_res.draw_time_line(b1_x=x_axis, b1_y=b1_time, b2_x=x_axis, b2_y=b2_time, b3_x=x_axis, b3_y=our_time,
                           x_label="Number of trees", y_label="Time span (seconds)")


def level_ratio() -> None:
    print('Performance with level ratio')

    opt_cost = []
    b1_cost = []
    b2_cost = []
    our_cost = []
    b1_time = []
    b2_time = []
    our_time = []

    for lvl_ratio in range(1, 11):
        print('Processing level ratio {tree}'.format(tree=lvl_ratio/10))
        b1_sess = []
        b2_sess = []
        our_sess = []
        opt_sess = []
        time_1 = []
        time_2 = []
        time_3 = []
        n_tree = 5
        for _ in range(0, 16):
            video_dependency = {}
            video_id_map_needed = {}
            start_id = 0
            first_level_num = 4
            second_level_num = first_level_num * lvl_ratio
            second_level_group = 3
            for tree_id in range(0, n_tree):
                this_video_dependency, this_video_id_map_needed = generate_tree(id_start=start_id,
                                                                                first_level_num=first_level_num,
                                                                                second_level_num=second_level_num)
                video_dependency.update(this_video_dependency)
                video_id_map_needed.update(this_video_id_map_needed)
                start_id += first_level_num + second_level_num

            # b1
            time_consumed, total_videos = baseline_1(num_user=30,
                                                     num_video_per_batch=(first_level_num +
                                                                          second_level_num * second_level_group) * n_tree)
            b1_sess.append(total_videos)
            time_1.append(time_consumed)

            # b2
            time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[first_level_num * n_tree,
                                                                                             second_level_num * n_tree])
            b2_sess.append(total_videos)
            time_2.append(time_consumed)

            # ours
            time_consumed, total_videos = ours(video_dependency=video_dependency,
                                               video_id_map_needed=video_id_map_needed, max_num_videos=50,
                                               spend_scale=0.6, max_active_user=60)
            our_sess.append(total_videos)
            time_3.append(time_consumed)

            opt_sess.append(sum(video_id_map_needed.values()))

        opt_cost.append(sum(opt_sess) / len(opt_sess))
        our_cost.append(sum(our_sess) / len(our_sess))
        b1_cost.append(sum(b1_sess) / len(b1_sess))
        b2_cost.append(sum(b2_sess) / len(b2_sess))

        b1_time.append(sum(time_1) / len(time_1))
        b2_time.append(sum(time_2) / len(time_2))
        our_time.append(sum(time_3) / len(time_3))

    x_axis = list(range(1, 11))
    sim_res.draw_sess_line(b1_x=x_axis, b1_y=b1_cost, b2_x=x_axis, b2_y=b2_cost, b3_x=x_axis, b3_y=our_cost,
                           b4_x=x_axis, b4_y=opt_cost, x_label="level_2_videos/level_1_videos", y_label="Number of sessions")
    sim_res.draw_time_line(b1_x=x_axis, b1_y=b1_time, b2_x=x_axis, b2_y=b2_time, b3_x=x_axis, b3_y=our_time,
                           x_label="level_2_videos/level_1_videos", y_label="Time span (seconds)")


def cost_scale() -> None:
    print('With cost scale')

    opt_cost = []
    b1_cost = []
    b2_cost = []
    our_cost = []
    b1_time = []
    b2_time = []
    our_time = []

    for c_scale in range(1, 11):
        print('Processing cost scale {tree}'.format(tree=c_scale/10))
        b1_sess = []
        b2_sess = []
        our_sess = []
        opt_sess = []
        time_1 = []
        time_2 = []
        time_3 = []
        n_tree = 3
        for _ in range(0, 16):
            video_dependency = {}
            video_id_map_needed = {}
            start_id = 0
            first_level_num = 2
            second_level_num = first_level_num * 4
            second_level_group = 3
            for tree_id in range(0, n_tree):
                this_video_dependency, this_video_id_map_needed = generate_tree(id_start=start_id,
                                                                                first_level_num=first_level_num,
                                                                                second_level_num=second_level_num)
                video_dependency.update(this_video_dependency)
                video_id_map_needed.update(this_video_id_map_needed)
                start_id += first_level_num + second_level_num

            # b1
            time_consumed, total_videos = baseline_1(num_user=30,
                                                     num_video_per_batch=(first_level_num +
                                                                          second_level_num * second_level_group) * n_tree)
            b1_sess.append(total_videos)
            time_1.append(time_consumed)

            # b2
            time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[first_level_num * n_tree,
                                                                                             second_level_num * n_tree])
            b2_sess.append(total_videos)
            time_2.append(time_consumed)

            # ours
            time_consumed, total_videos = ours(video_dependency=video_dependency,
                                               video_id_map_needed=video_id_map_needed, max_num_videos=50,
                                               spend_scale=c_scale/10, max_active_user=100)
            our_sess.append(total_videos)
            time_3.append(time_consumed)

            opt_sess.append(sum(video_id_map_needed.values()))

        opt_cost.append(sum(opt_sess) / len(opt_sess))
        our_cost.append(sum(our_sess) / len(our_sess))
        b1_cost.append(sum(b1_sess) / len(b1_sess))
        b2_cost.append(sum(b2_sess) / len(b2_sess))

        b1_time.append(sum(time_1) / len(time_1))
        b2_time.append(sum(time_2) / len(time_2))
        our_time.append(sum(time_3) / len(time_3))

    x_axis = list(range(1, 11))
    x_axis = [ele/10 for ele in x_axis]
    sim_res.draw_sess_line(b1_x=x_axis, b1_y=b1_cost, b2_x=x_axis, b2_y=b2_cost, b3_x=x_axis, b3_y=our_cost,
                           b4_x=x_axis, b4_y=opt_cost, x_label="cost_scale", y_label="Number of sessions")
    sim_res.draw_time_line(b1_x=x_axis, b1_y=b1_time, b2_x=x_axis, b2_y=b2_time, b3_x=x_axis, b3_y=our_time,
                           x_label="cost_scale", y_label="Time span (seconds)")

def max_user_num() -> None:
    print('Max number of current users')

    opt_cost = []
    b1_cost = []
    b2_cost = []
    our_cost = []
    b1_time = []
    b2_time = []
    our_time = []

    for max_num in range(30, 120, 10):
        print('Processing max user num {tree}'.format(tree=max_num))
        b1_sess = []
        b2_sess = []
        our_sess = []
        opt_sess = []
        time_1 = []
        time_2 = []
        time_3 = []
        n_tree = 3
        for _ in range(0, 16):
            video_dependency = {}
            video_id_map_needed = {}
            start_id = 0
            first_level_num = 2
            second_level_num = first_level_num * 4
            second_level_group = 3
            for tree_id in range(0, n_tree):
                this_video_dependency, this_video_id_map_needed = generate_tree(id_start=start_id,
                                                                                first_level_num=first_level_num,
                                                                                second_level_num=second_level_num)
                video_dependency.update(this_video_dependency)
                video_id_map_needed.update(this_video_id_map_needed)
                start_id += first_level_num + second_level_num

            # b1
            time_consumed, total_videos = baseline_1(num_user=30,
                                                     num_video_per_batch=(first_level_num +
                                                                          second_level_num * second_level_group) * n_tree)
            b1_sess.append(total_videos)
            time_1.append(time_consumed)

            # b2
            time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[first_level_num * n_tree,
                                                                                             second_level_num * n_tree])
            b2_sess.append(total_videos)
            time_2.append(time_consumed)

            # ours
            time_consumed, total_videos = ours(video_dependency=video_dependency,
                                               video_id_map_needed=video_id_map_needed, max_num_videos=50,
                                               spend_scale=0.5, max_active_user=max_num)
            our_sess.append(total_videos)
            time_3.append(time_consumed)

            opt_sess.append(sum(video_id_map_needed.values()))

        opt_cost.append(sum(opt_sess) / len(opt_sess))
        our_cost.append(sum(our_sess) / len(our_sess))
        b1_cost.append(sum(b1_sess) / len(b1_sess))
        b2_cost.append(sum(b2_sess) / len(b2_sess))

        b1_time.append(sum(time_1) / len(time_1))
        b2_time.append(sum(time_2) / len(time_2))
        our_time.append(sum(time_3) / len(time_3))

    x_axis = list(range(30, 120, 10))
    sim_res.draw_sess_line(b1_x=x_axis, b1_y=b1_cost, b2_x=x_axis, b2_y=b2_cost, b3_x=x_axis, b3_y=our_cost,
                           b4_x=x_axis, b4_y=opt_cost, x_label="max user num", y_label="Number of sessions")
    sim_res.draw_time_line(b1_x=x_axis, b1_y=b1_time, b2_x=x_axis, b2_y=b2_time, b3_x=x_axis, b3_y=our_time,
                           x_label="max user num", y_label="Time span (seconds)")


def view_needed_variance() -> None:
    print('Variance of view needed')

    opt_cost = []
    b1_cost = []
    b2_cost = []
    our_cost = []
    b1_time = []
    b2_time = []
    our_time = []

    for view_var in range(11, 31):
        print('Processing variance of view needed {tree}'.format(tree=view_var))
        b1_sess = []
        b2_sess = []
        our_sess = []
        opt_sess = []
        time_1 = []
        time_2 = []
        time_3 = []
        n_tree = 3
        for _ in range(0, 16):
            video_dependency = {}
            video_id_map_needed = {}
            start_id = 0
            first_level_num = 4
            second_level_num = first_level_num * 4
            second_level_group = 3
            for tree_id in range(0, n_tree):
                this_video_dependency, this_video_id_map_needed = generate_tree(id_start=start_id,
                                                                                first_level_num=first_level_num,
                                                                                second_level_num=second_level_num, rating_low=view_var)
                video_dependency.update(this_video_dependency)
                video_id_map_needed.update(this_video_id_map_needed)
                start_id += first_level_num + second_level_num

            # b1
            time_consumed, total_videos = baseline_1(num_user=30,
                                                     num_video_per_batch=(first_level_num +
                                                                          second_level_num * second_level_group) * n_tree)
            b1_sess.append(total_videos)
            time_1.append(time_consumed)

            # b2
            time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[first_level_num * n_tree,
                                                                                             second_level_num * n_tree])
            b2_sess.append(total_videos)
            time_2.append(time_consumed)

            # ours
            time_consumed, total_videos = ours(video_dependency=video_dependency,
                                               video_id_map_needed=video_id_map_needed, max_num_videos=50,
                                               spend_scale=0.5, max_active_user=60)
            our_sess.append(total_videos)
            time_3.append(time_consumed)

            opt_sess.append(sum(video_id_map_needed.values()))

        opt_cost.append(sum(opt_sess) / len(opt_sess))
        our_cost.append(sum(our_sess) / len(our_sess))
        b1_cost.append(sum(b1_sess) / len(b1_sess))
        b2_cost.append(sum(b2_sess) / len(b2_sess))

        b1_time.append(sum(time_1) / len(time_1))
        b2_time.append(sum(time_2) / len(time_2))
        our_time.append(sum(time_3) / len(time_3))

    x_axis = list(range(11, 31))

    sim_res.draw_sess_line(b1_x=x_axis, b1_y=b1_cost, b2_x=x_axis, b2_y=b2_cost, b3_x=x_axis, b3_y=our_cost,
                           b4_x=x_axis, b4_y=opt_cost, x_label="view needed lower bound", y_label="Number of sessions")
    sim_res.draw_time_line(b1_x=x_axis, b1_y=b1_time, b2_x=x_axis, b2_y=b2_time, b3_x=x_axis, b3_y=our_time,
                           x_label="view needed lower bound", y_label="Time span (seconds)")

def sys_main() -> None:
    # enumerate_trees()
    level_ratio()
    # cost_scale()
    # max_user_num()
    # view_needed_variance()

# b1_cost = []
# b2_cost = []
# ours_cost = []
# opt_cost = []
#
# b1_time = []
# b2_time = []
# our_time = []
#
# for _ in range(0, 16):
#     # video_dependency = {1: {6, 7, 8, 15, 16, 17}, 2: {6, 7, 8, 15, 16, 17}, 3: {9, 10, 11, 18, 19, 20},
#     #                     4: {9, 10, 11, 18, 19, 20}, 5: {12, 13, 14, 21, 22, 23}, 6: set(), 7: set(),
#     #                     8: set(), 9: set(), 10: set(), 11: set(), 12: set(), 13: set(), 14: set(), 15: set(),
#     #                     16: set(), 17: set(), 18: set(), 19: set(), 20: set(), 21: set(), 22: set(), 23: set()}
#     # video_id_map_needed = {}
#     # opt = 0
#     # for i in range(1, 24):
#     #     video_id_map_needed[i] = random.randint(11, 30)
#     #     opt += video_id_map_needed[i]
#
#     video_dependency = {1: {6, 7, 8, 9, 10, 11}, 2: {6, 7, 8, 9, 10, 11}, 6: set(), 7: set(),
#                         8: set(), 9: set(), 10: set(), 11: set()}
#     video_id_map_needed = {}
#     opt = 0
#     for i in range(1, 12):
#         if i in video_dependency:
#             video_id_map_needed[i] = random.randint(11, 30)
#             opt += video_id_map_needed[i]
#     opt_cost.append(opt)
#
#     print('OPT viewed', opt)
#     time_consumed, total_videos = baseline_1(num_user=30, num_video_per_batch=41)
#     # time_consumed, total_videos = baseline_1(num_user=30, num_video_per_batch=17)
#
#     b1_cost.append(total_videos)
#     b1_time.append(time_consumed)
#
#     time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[5, 18])
#     # time_consumed, total_videos = baseline_2(num_user=[30, 30], num_video_per_batch=[2, 6])
#
#     b2_cost.append(total_videos)
#     b2_time.append(time_consumed)
#
#     time_consumed, total_videos = ours(video_dependency=video_dependency, video_id_map_needed=video_id_map_needed)
#     ours_cost.append(total_videos)
#     our_time.append(time_consumed)
#
# sim_res.draw_time_cost(b1=b1_time, b2=b2_time, our=our_time)
# sim_res.draw_video_cost(b1=b1_cost, b2=b2_cost, our=ours_cost, opt=opt_cost)


if __name__ == '__main__':
    print('Start experiments')
    sys_main()
