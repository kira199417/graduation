# -*- coding: utf-8 -*-

import json

from myredis import myredis
from similarity import compond_movie, item_similarity
from db.orm import fetch_user_and_movie_and_interest


if __name__ == '__main__':
    data_set = fetch_user_and_movie_and_interest()
    W = item_similarity(compond_movie(data_set))
    for movie, related_movies in W.items():
        myredis.set(movie, json.dumps(related_movies))
        myredis.expire(movie, 3600)
        del W[movie]