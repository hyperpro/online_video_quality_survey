from abc import ABC
from typing import Tuple

from simulator_base import PerfSimulator
import utils
from events import Event, EventType, User, VideoTopo


class OurSimulator(PerfSimulator, ABC):

    def __init__(self, max_user_num: int, n_video_per_batch: int, video_topo: VideoTopo) -> None:
        super().__init__()
        self.max_user_num = max_user_num
        self.n_video_per_batch = n_video_per_batch
        self.video_topo = video_topo

    def execute_recruiting(self, event) -> None:
        event.start_time += 0  # 0 is a magic number, meaning that how much time a user can connect to our website
        event.event_type = EventType.TRAINING
        self.add_event(event=event)

    def execute_watch_videos(self, event) -> None:
        this_user = self.get_user_from_event(event)
        if event.last_video_id != -1:
            this_user.watched_video_set.add(event.last_video_id)
            self.video_topo.after_video_watched(event.last_video_id)

        event.last_video_id = self.video_topo.get_next_video(this_user.watched_video_set)

        # when to stop
        if this_user.num_watched_videos < self.n_video_per_batch and event.last_video_id is not None:
            watch_time = utils.watch_each_video_time()
            event.start_time += watch_time
            self.time_consumed = max(self.time_consumed, event.start_time)
            this_user.num_watched_videos += 1
            self.add_event(event=event)

    def execute_training(self, event) -> None:
        this_user = self.get_user_from_event(event)
        training_time = utils.watch_tutorial_time()
        this_user.is_done_training = True
        event.start_time += training_time
        event.event_type = EventType.WATCH_VIDEO
        event.last_video_id = -1
        self.add_event(event=event)

    def run(self) -> tuple[int, int]:

        # recruit users
        for i in range(0, self.max_user_num):
            i_th_user_offset = utils.time_delta_recruiting_i_th_worker(i)
            new_user = User(user_id=i, num_watched_videos=0,
                            is_done_training=False, start_time=self.time_consumed)
            self.user_id_map_object[i] = new_user
            recruit_event = Event(start_time=self.time_consumed + i_th_user_offset,
                                  event_type=EventType.RECRUITING, user_id=i)
            self.add_event(recruit_event)

        # run events
        while len(self.event_q) > 0:
            self.execute_top_event()

        total_videos = 0
        for i in range(0, self.max_user_num):
            total_videos += self.user_id_map_object[i].num_watched_videos
        self.total_videos = total_videos

        for user in self.user_id_map_object:
            print(user, len(self.user_id_map_object[user].watched_video_set), self.user_id_map_object[user].watched_video_set)
        return self.time_consumed, total_videos
