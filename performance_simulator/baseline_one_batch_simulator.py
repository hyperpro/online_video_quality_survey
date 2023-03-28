import os
import sys
from abc import ABC
from simulator_base import PerfSimulator
import utils
from events import Event, EventType, User


class OneBatchSimulator(PerfSimulator, ABC):

    def __init__(self, n_user_per_batch: int, n_video_per_batch: int) -> None:
        super().__init__()
        self.n_user_per_batch = n_user_per_batch
        self.n_video_per_batch = n_video_per_batch

    def execute_recruiting(self, event) -> None:
        event.start_time += 0  # 0 is a magic number, meaning that how much time a user can connect to our website
        event.event_type = EventType.TRAINING
        self.add_event(event=event)

    def execute_watch_videos(self, event) -> None:
        this_user = self.get_user_from_event(event)
        watch_time = utils.watch_each_video_time()
        this_user.num_watched_videos += 1
        event.start_time += watch_time
        self.time_consumed = max(self.time_consumed, event.start_time)
        if this_user.num_watched_videos < self.n_video_per_batch:
            self.add_event(event=event)

    def execute_training(self, event) -> None:
        this_user = self.get_user_from_event(event)
        training_time = utils.watch_tutorial_time()
        this_user.is_done_training = True
        event.start_time += training_time
        event.event_type = EventType.WATCH_VIDEO
        self.add_event(event=event)

    def run(self) -> tuple[int, int]:
        # recruit users
        for i in range(0, self.n_user_per_batch):
            i_th_user_offset = utils.time_delta_recruiting_i_th_worker(i)
            # suppose starting time is 0
            new_user = User(user_id=i, num_watched_videos=0, is_done_training=False)
            self.user_id_map_object[i] = new_user
            recruit_event = Event(start_time=i_th_user_offset, event_type=EventType.RECRUITING, user_id=i)
            self.add_event(recruit_event)

        # run events
        while len(self.event_q) > 0:
            self.execute_top_event()

        total_videos = 0
        for i in range(0, self.n_user_per_batch):
            total_videos += self.user_id_map_object[i].num_watched_videos
        self.total_videos = total_videos

        return self.time_consumed, self.total_videos

