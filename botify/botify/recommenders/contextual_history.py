import random
from collections import defaultdict
from typing import List
from .contextualtop import ContextualOrTop
from .recommender import Recommender
from ..track import Catalog


class MyRecommender(Recommender):
    def __init__(self, tracks_redis, my_recommends, catalog: Catalog):
        self.fallback = ContextualOrTop(tracks_redis, catalog)
        self.tracks = my_recommends
        self.catalog = catalog
        self.users_favorite = defaultdict(list)
        self.users_listened = defaultdict(set)
        self.users_listened_art = defaultdict(set)
    
    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        self.users_listened[user].add(prev_track)
        previous_track = self.tracks.get(prev_track)

        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        track_info = self.catalog.from_bytes(previous_track)
        self.users_listened_art[user].add(track_info.artist)

        if prev_track_time < 0.8:
            if len(self.users_favorite[user]) > 0:
                prev_track = self.users_favorite[user][-1]
                previous_track = self.tracks.get(prev_track)
                track_info = self.catalog.from_bytes(previous_track)
        else:
            self.users_favorite[user].append(prev_track)

        recommendations = track_info.recommendations

        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        return self._next(user, list(recommendations))
    
    def _next(self, user, recommendations: List[int]) -> int:
        shuffled = list(recommendations)
        random.shuffle(shuffled)

        for track in shuffled[:10]:
            if track in self.users_listened[user]:
                continue

            b_track_info = self.tracks.get(track)
            if b_track_info is None:
                continue

            track_info = self.catalog.from_bytes(b_track_info)
            if track_info.artist in self.users_listened_art:
                continue

            return track

        return shuffled[-1]