from abc import ABC
from typing import Tuple, Dict
from simulator_base import PerfSimulator
import utils
from events import Event, VideoTopo
import networkx as nx
import random


class OurSimulator(PerfSimulator, ABC):

    def __init__(self, max_num_videos: int, video_topo: VideoTopo, cost_scale: float, max_active_user: int = 60) -> None:
        super().__init__()
        self.max_num_videos = max_num_videos
        self.video_topo = video_topo
        # cost_scale ranging from 0 to 1
        self.cost_scale = cost_scale
        self.max_active_user = max_active_user

    def execute_watch_videos(self, event: Event) -> None:
        this_user = self.get_user_from_event(event)
        if event.last_video_id != -1:
            this_user.watched_video_set.add(event.last_video_id)
            self.video_topo.after_video_watched(event.last_video_id)

        avail_video_dict = self.video_topo.get_next_video(this_user.watched_video_set)

        if avail_video_dict is not None:
            # if we need more users, hire them
            self.recruit_users_on_demand(video_view_dict=avail_video_dict)
            # randomly select a video to watch
            event.last_video_id = random.choice(list(avail_video_dict.keys()))
        else:
            event.last_video_id = None

        watch_time = utils.watch_each_video_time()
        event.start_time += watch_time

        # let the user watch more videos or just stop
        if this_user.num_watched_videos < self.max_num_videos and event.last_video_id is not None:
            self.time_consumed = max(self.time_consumed, event.start_time)
            this_user.num_watched_videos += 1
            self.add_event(event=event)
        else:
            # End it
            this_user.end_time = event.start_time
            self.active_users.remove(this_user.user_id)

    def recruit_users_on_demand(self, video_view_dict: Dict[int, int]) -> None:
        # calculate minimum user number
        min_extra_user_needed_for_videos = []
        for video_id in video_view_dict:
            num_user_watched = 0
            for user_id in self.active_users:
                if video_id in self.user_id_map_object[user_id].watched_video_set:
                    num_user_watched += 1

            if self.active_user_num() - num_user_watched < video_view_dict[video_id]:
                min_extra_user_needed_for_videos.append(
                    video_view_dict[video_id] - self.active_user_num() + num_user_watched)
            else:
                min_extra_user_needed_for_videos.append(0)

        min_user_num = len(video_view_dict)
        if max(min_extra_user_needed_for_videos) > 0:
            min_user_num = self.active_user_num() + max(min_extra_user_needed_for_videos)

        # calculate maximal user number
        total_view_needed = 0
        for video_id in video_view_dict:
            total_view_needed += video_view_dict[video_id]
        if self.active_user_num() == 0:
            max_user_needed = total_view_needed
        else:
            # USE MAX MATCHING TO ACCURATELY CALCULATE -- very slow
            # graph = nx.Graph()
            # graph.add_nodes_from(['U' + str(user_id) for user_id in self.active_users], bipartite=0)
            # graph.add_nodes_from(['V' + str(video_id) for video_id in video_view_dict], bipartite=1)
            #
            # user_nodes = set()
            # for video_id in video_view_dict:
            #     for user_id in self.active_users:
            #         if video_id not in self.user_id_map_object[user_id].watched_video_set:
            #             graph.add_edge('U' + str(user_id), 'V' + str(video_id))
            #             user_nodes.add('U' + str(user_id))
            #
            # matching_count = len(nx.algorithms.bipartite.maximum_matching(graph, top_nodes=list(user_nodes)))
            # total_view_needed = 0
            # for video_id in video_view_dict:
            #     total_view_needed += video_view_dict[video_id]
            # max_user_needed = total_view_needed + self.active_user_num() - matching_count

            # use rough estimate
            total_view_needed = 0
            for video_id in video_view_dict:
                total_view_needed += video_view_dict[video_id]
            max_user_needed = total_view_needed + self.active_user_num()

        # calculate how many more users we need
        users_needed = int((max_user_needed - min_user_num) * self.cost_scale) + min_user_num
        if users_needed > self.active_user_num() and self.active_user_num() < 40: # 40 means the limitation of masters
            # recruit users
            for i in range(0, min(users_needed - self.active_user_num(), self.max_active_user - self.active_user_num())):
                self.create_recruiting_event(start_time=self.time_consumed, i_th_in_batch=i)

    def run(self) -> Tuple[int, int]:

        # Initialize the simulator
        self.recruit_users_on_demand(video_view_dict=self.video_topo.get_next_video(already_watched=set()))

        # run events
        while len(self.event_q) > 0:
            self.execute_top_event()

        # update self.total_videos
        self.cal_total_video_sessions_viewed()
        return self.time_consumed, self.total_videos
