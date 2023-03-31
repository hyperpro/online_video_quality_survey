from abc import ABC
from simulator_base import PerfSimulator
import utils
from events import Event


class OneBatchSimulator(PerfSimulator, ABC):

    def __init__(self, n_user_per_batch: int, n_video_per_batch: int) -> None:
        super().__init__()
        self.n_user_per_batch = n_user_per_batch
        self.n_video_per_batch = n_video_per_batch

    def execute_watch_videos(self, event: Event) -> None:
        this_user = self.get_user_from_event(event)
        watch_time = utils.watch_each_video_time()
        this_user.num_watched_videos += 1
        event.start_time += watch_time
        self.time_consumed = max(self.time_consumed, event.start_time)
        if this_user.num_watched_videos < self.n_video_per_batch:
            self.add_event(event=event)
        else:
            # End it
            this_user.end_time = event.start_time
            self.active_users.remove(this_user.user_id)


    def run(self) -> tuple[int, int]:
        # recruit users
        for i in range(0, self.n_user_per_batch):
            self.create_recruiting_event(start_time=0, i_th_in_batch=i)

        # run events
        while len(self.event_q) > 0:
            self.execute_top_event()

        # update self.total_videos
        self.cal_total_video_sessions_viewed()

        return self.time_consumed, self.total_videos
