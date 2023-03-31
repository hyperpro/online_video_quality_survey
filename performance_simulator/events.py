import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Set
import collections


class EventType(Enum):
    WATCH_VIDEO = 1
    TRAINING = 2
    RECRUITING = 3


@dataclass
class Event:
    start_time: int = field(default=0)
    event_type: EventType = field(default_factory=EventType)
    end_time: int = field(default=0)
    user_id: int = field(default=-1)
    last_video_id: int = field(default=-1)

    def __gt__(self, other):
        return self.start_time > other.start_time

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __le__(self, other):
        return self.start_time <= other.start_time

    def __ge__(self, other):
        return self.start_time >= other.start_time


@dataclass
class User:
    user_id: int = field(default=0)
    i_th_in_batch: int = field(default=0)
    start_time: int = field(default=0)
    end_time: int = field(default=0)
    num_watched_videos: int = field(default=0)
    is_done_training: bool = field(default=False)
    watched_video_set: Set[int] = field(default_factory=set)


@dataclass
class VideoTopo:
    """
    The input logic of users
    """
    video_dependency: Dict[int, Set[int]] = field(default_factory=Dict)
    video_id_map_needed: Dict[int, int] = field(default_factory=Dict)

    def __post_init__(self) -> None:
        self.video_id_map_view_time = collections.defaultdict(int)
        self.in_degree_map_video_set = collections.defaultdict(set)
        self.video_id_map_in_degree = collections.defaultdict(int)

        for video_id in self.video_dependency:
            for vid in self.video_dependency[video_id]:
                self.video_id_map_in_degree[vid] += 1

        for video_id in self.video_dependency:
            self.in_degree_map_video_set[self.video_id_map_in_degree[video_id]].add(video_id)

    def get_next_video(self, already_watched: Set[int]) -> Dict[int, int] | None:
        candidate_set = {}
        for video_id in self.in_degree_map_video_set[0]:
            if video_id not in already_watched and \
                    self.video_id_map_view_time[video_id] < self.video_id_map_needed[video_id]:
                candidate_set[video_id] = self.video_id_map_needed[video_id] - self.video_id_map_view_time[video_id]

        if len(candidate_set) == 0:
            # No videos are selected
            return None
        else:
            # randomly select a video to rate
            return candidate_set

    def after_video_watched(self, video_id: int) -> None:
        self.video_id_map_view_time[video_id] += 1
        # if the video has been viewed enough times
        if self.video_id_map_view_time[video_id] >= self.video_id_map_needed[video_id]:
            for dependent_id in self.video_dependency[video_id]:
                old_in_degree = self.video_id_map_in_degree[dependent_id]
                new_in_degree = old_in_degree - 1
                if new_in_degree >= 0:
                    self.in_degree_map_video_set[old_in_degree].remove(dependent_id)
                    self.in_degree_map_video_set[new_in_degree].add(dependent_id)
                    self.video_id_map_in_degree[dependent_id] = new_in_degree
