import random

from .toppop import TopPop
from .recommender import Recommender
from ..track import Catalog


class ContextualOrTop(Recommender):  
    def __init__(self, tracks_redis, catalog: Catalog):
        self.tracks_redis = tracks_redis
        self.fallback = TopPop(tracks_redis, catalog.top_tracks)
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]
