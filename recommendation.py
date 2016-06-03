# -*- coding: utf-8 -*-

import json
import random
from operator import itemgetter

from db.orm import fetch_user_and_movie_and_interest
from myredis import myredis


K = 8


def split_data(data, M, k, seed):
    test = []
    train = []
    random.seed(seed)
    for user, item, interest in data:
        if random.randint(0, M) == k:
            test.append((user, item, interest))
        else:
            train.append((user, item, interest))
    return train, test


def compond_user_movie_interest(user_movie_interest):
    d = dict()
    for user, item, interest in user_movie_interest:
        d[item] = interest
    return d


def recall(train, test, W):
    hit = 0
    all = 0
    com_test = compond_movie(test)
    com_train = compond_movie(train)
    for user in com_train.keys():
        if user not in com_test:
            continue
        tu = com_test[user]
        rec_movies = recommendation(train, user, W, K)
        for item in rec_movies:
            if item[0] in tu:
                hit += 1
        all += len(tu)
    print 'recall hit: %s' % hit
    return hit / (all * 1.0)


def precision(train, test, W):
    hit = 0
    all = 0
    com_test = compond_movie(test)
    com_train = compond_movie(train)
    for user in com_train.keys():
        if user not in com_test:
            continue
        tu = com_test[user]
        rec_movies = recommendation(train, user, W, K)
        for item in rec_movies:
            if item[0] in tu:
                hit += 1
        all += K
    print 'precision hit: %s' % hit
    return hit / (all * 1.0)


def recommendation(train, user_id):
    rank = dict()
    user_movie_interest = list()
    for item in train:
        if item[0] == user_id:
            user_movie_interest.append(item)
    ru = compond_user_movie_interest(user_movie_interest)
    for i, pi in ru.items():
        related_movies = myredis.get(i)
        if not related_movies:
            continue
        related_movies = json.loads(related_movies)
        for j, wj in sorted(related_movies.items(),
                key=itemgetter(1), reverse=True)[0:K]:
            if j in ru:
                continue

            if j not in rank:
                rank[j] = {}

            rank[j]['value'] = rank[j].get('value', 0) + pi * wj

            if 'reason' not in rank[j]:
                rank[j]['reason'] = []
            rank[j]['reason'].append(i)

    return sorted(rank.iteritems(), key=lambda x: x[1]['value'], reverse=True)


def recommend(user_id):
    rank = dict()
    ru = compond_user_movie_interest(fetch_user_and_movie_and_interest(user_id))
    for i, pi in ru.items():
        related_movies = myredis.get(i)
        if not related_movies:
            continue
        related_movies = json.loads(related_movies)
        for j, wj in sorted(related_movies.items(),
                key=itemgetter(1), reverse=True)[0:K]:
            if j in ru:
                continue

            if j not in rank:
                rank[j] = {}

            rank[j]['value'] = rank[j].get('value', 0) + pi * wj

            if 'reason' not in rank[j]:
                rank[j]['reason'] = []
            rank[j]['reason'].append(i)

    return sorted(rank.iteritems(), key=lambda x: x[1]['value'], reverse=True)


if __name__ == '__main__':
    train, test = split_data(fetch_user_and_movie_and_interest(), 8, 6, 2)
    com_train = compond_movie(train)
    W = item_similarity(com_train)
    for movie, related_movies in W.items():
        myredis.set(movie, json.dumps(related_movies))
        myredis.expire(movie, 3600)
        del W[movie]
    del com_train
    print 'recall: %s' % recall(train, test, W)
    print 'precision: %s' % precision(train, test, W)