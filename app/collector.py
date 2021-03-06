#!/usr/bin/env python
#
# Copyright (c) 2018-2020 William Chanrico.
#
# This file is part of follower-gender-classification
# (see https://github.com/williamchanrico/follower-gender-classification).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# -*- coding: utf-8 -*-

import time
import math
import random


def get_all_followers_comments(client,
                               username,
                               follower_limit=math.inf,
                               media_per_follower_limit=25,
                               comments_per_media_limit=250):
    all_follower_comments = []
    followers = get_followers_id_list(client, username, follower_limit)

    for follower in followers:
        follower_comments = []

        all_media_id = get_all_media_id(client, follower,
                                        media_per_follower_limit)
        for media_id in all_media_id:
            media_comments = get_media_comments(client, media_id,
                                                comments_per_media_limit)
            follower_comments.extend(media_comments)

        all_follower_comments.append(follower_comments)

    random.shuffle(all_follower_comments)
    return all_follower_comments


def get_followers_id_list(client, username, limit=10000):
    """ Returns list of followers' user ID """
    followers = []

    next_max_id = ''
    while True:
        client.searchUsername(username)
        user_id = client.LastJson["user"]["pk"]
        client.getUserFollowers(user_id, maxid=next_max_id)

        data = filter(lambda x: x['is_private'] == False,
                      client.LastJson.get('users', []))
        data = map(lambda x: x['pk'], data)
        followers.extend(data)

        next_max_id = client.LastJson.get('next_max_id', '')
        if not next_max_id or len(followers) >= limit:
            random.shuffle(followers)
            if len(followers) > limit:
                del followers[limit:]
            break

    return followers


def get_all_media_id(client, user_id, media_limit):
    client.getUserFeed(user_id)

    media_id_list = client.LastJson['items']
    media_id_list = list(map(lambda x: x['id'], media_id_list))
    random.shuffle(media_id_list)

    if len(media_id_list) > media_limit:
        del media_id_list[media_limit:]

    return media_id_list


def get_media_comments(client, media_id, comment_limit):
    media_comments = []

    max_id = ''
    while True:
        client.getMediaComments(media_id, max_id=max_id)
        try:
            comments = reversed(client.LastJson['comments'])
            comments = map(lambda x: x['text'].lower(), comments)

            media_comments.extend(comments)
        except:
            break

        has_more_comments = client.LastJson.get('has_more_comments', False)
        if not has_more_comments or len(media_comments) >= comment_limit:
            if len(media_comments) > comment_limit:
                del media_comments[comment_limit:]
            break

        max_id = client.LastJson.get('next_max_id', '')
        time.sleep(1)

    return media_comments


def get_user_id(client, username):
    client.searchUsername(username)
    try:
        user_id = client.LastJson["user"]["pk"]
    except:
        pass

    return user_id


def get_user_data(client, username):
    client.searchUsername(username)
    try:
        user = client.LastJson["user"]
    except:
        pass

    return user
