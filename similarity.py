# -*- coding: utf-8 -*-

import math

def compond_movie(data_set):
    d = dict()
    for user, item, interest in data_set:
        if user not in d:
            d[user] = list()
        d[user].append(item)
    return d


def item_similarity(data_set):
    # calculate co-rated users between items
    C = dict()
    N = dict()
    for u, items in data_set.items():
        for i in items:
            N[i] = N.get(i, 0) + 1
            if i not in C:
                C[i] = dict()
            for j in items: 
                if i == j:
                    continue
                C[i][j] = C[i].get(j, 0) + (1 / math.log(1 + len(items) * 1.0))
    # calculate finial similarity matrix W
    for i, related_items in C.items():
        for j, cij in related_items.items():
            if cij < 3:
                del C[i][j]
        if C[i] == {}:
            del C[i]

    W = dict()
    for i, related_items in C.items():
        if i not in W:
            W[i] = {}
        for j, cij in related_items.items():
            W[i][j] = cij / math.sqrt(N[i] * N[j])
    return W