import sys
import os
import heapq
from events import Event, EventType, User
from abc import ABCMeta, abstractmethod


class PerfSimulator(metaclass=ABCMeta):

    def __init__(self) -> None:
        self.event_q = []
        self.user_id_map_object = {}
        self.total_videos = 0
        self.time_consumed = 0

    def add_event(self, event: Event) -> None:
        heapq.heappush(self.event_q, event)

    def get_user_from_event(self, event: Event) -> User:
        return self.user_id_map_object[event.user_id]

    @abstractmethod
    def execute_recruiting(self, event):
        pass

    @abstractmethod
    def execute_watch_videos(self, event):
        pass

    @abstractmethod
    def execute_training(self, event) -> int:
        pass

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

    @abstractmethod
    def run(self) -> int:
        pass
