# -*- coding: utf-8 -*-

import redis


myredis = redis.StrictRedis(host='localhost', port=6379, db=0)