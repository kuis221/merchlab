#!/usr/bin/python
# -*- coding: utf-8 -*-
import tweepy
import json

consumer_key = 'Z8OFE6tAsQdQqZYfy1wMOqGHj'
consumer_secret = 'SzLYO6EYKjxgQE9zsuc1igts8GFlHLdWaCmAGEBmsmvnXrS06D'
access_token = '224849539-IYLhQNdMzBnZEsLnyaaXKJEeIK2YIZxVFYF20p8k'
access_token_secret = 'X44g7zJmJExZyWvDZfr8yoxdo5b29WoiT9XJj2VshT26q'
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
trends1 = api.trends_place(2450022)

print json.dumps(trends1, indent=4, sort_keys=True)