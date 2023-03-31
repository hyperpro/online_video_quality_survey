from abc import ABC
from simulator_base import PerfSimulator
import utils
from typing import List
from events import Event


class MultiBatchSimulator(PerfSimulator, ABC):

    def __init__(self, n_user_per_batch: List[int], n_video_per_batch: List[int]) -> None:
        super().__init__()
        self.n_user_per_batch = n_user_per_batch
        self.n_video_per_batch = n_video_per_batch
        self.cur_batch = 0

    def execute_watch_videos(self, event: Event) -> None:
        this_user = self.get_user_from_event(event)
        watch_time = utils.watch_each_video_time()
        this_user.num_watched_videos += 1
        event.start_time += watch_time
        self.time_consumed = max(self.time_consumed, event.start_time)
        if this_user.num_watched_videos < self.n_video_per_batch[self.cur_batch]:
            self.add_event(event=event)
        else:
            # End it
            this_user.end_time = event.start_time
            self.active_users.remove(this_user.user_id)

    def run(self) -> tuple[int, int]:
        batch_count = len(self.n_user_per_batch)
        for batch in range(0, batch_count):
            self.cur_batch = batch
            # update the start time of the next batch
            self.time_consumed += utils.gap_between_batches()

            # recruit users
            for i in range(0, self.n_user_per_batch[batch]):
                self.create_recruiting_event(start_time=self.time_consumed, i_th_in_batch=i)

            # run events
            while len(self.event_q) > 0:
                self.execute_top_event()

        # update self.total_videos
        self.cal_total_video_sessions_viewed()
        return self.time_consumed, self.total_videos
