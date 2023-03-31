import heapq
from events import Event, EventType, User
from abc import ABCMeta, abstractmethod
import utils


class PerfSimulator(metaclass=ABCMeta):

    def __init__(self) -> None:
        self.event_q = []
        self.user_id_map_object = {}
        self.cur_max_user_id = -1
        self.active_users = set()
        self.total_videos = 0
        self.time_consumed = 0

    def add_event(self, event: Event) -> None:
        heapq.heappush(self.event_q, event)

    def get_user_from_event(self, event: Event) -> User:
        return self.user_id_map_object[event.user_id]

    def execute_recruiting(self, event):
        this_user = self.get_user_from_event(event=event)
        time_spent_in_recruiting = utils.time_delta_recruiting_i_th_worker(i=this_user.i_th_in_batch)
        event.start_time += time_spent_in_recruiting
        event.event_type = EventType.TRAINING
        # update user info
        this_user.start_time = event.start_time
        self.active_users.add(this_user.user_id)
        # fire a new event for training period
        self.add_event(event=event)

    @abstractmethod
    def execute_watch_videos(self, event) -> None:
        pass

    def execute_training(self, event) -> None:
        this_user = self.get_user_from_event(event)
        training_time = utils.watch_tutorial_time()
        this_user.is_done_training = True
        event.start_time += training_time
        event.event_type = EventType.WATCH_VIDEO
        event.last_video_id = -1
        self.add_event(event=event)

    def execute_top_event(self) -> None:
        event = heapq.heappop(self.event_q)
        if event.event_type == EventType.WATCH_VIDEO:
            self.execute_watch_videos(event=event)
        elif event.event_type == EventType.RECRUITING:
            self.execute_recruiting(event=event)
        elif event.event_type == EventType.TRAINING:
            self.execute_training(event=event)
        else:
            raise NotImplemented("Unexpected event type")

    def create_recruiting_event(self, start_time: int, i_th_in_batch: int) -> None:
        self.cur_max_user_id += 1
        user_id = self.cur_max_user_id
        new_user = User(user_id=user_id, i_th_in_batch=i_th_in_batch, num_watched_videos=0,
                        is_done_training=False, start_time=start_time)
        self.user_id_map_object[user_id] = new_user
        recruit_event = Event(start_time=start_time,
                              event_type=EventType.RECRUITING, user_id=user_id)
        self.add_event(recruit_event)

    def cal_total_video_sessions_viewed(self) -> None:
        total_videos = 0
        for usr_id in self.user_id_map_object:
            total_videos += self.user_id_map_object[usr_id].num_watched_videos
        self.total_videos = total_videos

    def active_user_num(self) -> int:
        return len(self.active_users)

    @abstractmethod
    def run(self) -> int:
        pass
