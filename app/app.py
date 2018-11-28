#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import argparse
from base64 import b64encode
import time
import random
import json
from collections import Counter

from flask_socketio import SocketIO, emit
from threading import Thread, Event
from time import sleep
from flask import (Flask, render_template, flash, redirect,
    url_for, request, copy_current_request_context)

import cache
import collector
from naive_bayes import naive_bayes
from xgb import xgb
from adab import adab
from svm import svm
from thirdparty import InstagramAPI as ig
from scipy.sparse import coo_matrix, vstack

client_threads = {}
app = Flask("Instagram Follower Gender Classifier API")
socketio = SocketIO(app)

main_model = {}
list_of_words = {}
main_classifier = {}
compute_threshold = 0

BLACKLIST_WORDS = []

def load_blacklist_words(filename):
    global BLACKLIST_WORDS
    with open(filename) as f:
        BLACKLIST_WORDS = f.readlines()
    BLACKLIST_WORDS = [x.strip() for x in BLACKLIST_WORDS]


class ClientThread(Thread):
    def __init__(self, client_id):
        self._client_id = client_id
        super().__init__()


    def setData(self, algorithm, username, follower_limit, media_per_follower_limit, comments_per_media_limit):
        self._algorithm = algorithm
        self._username = username
        self._follower_limit = int(follower_limit)
        self._media_per_follower_limit = int(media_per_follower_limit)
        self._comments_per_media_limit = int(comments_per_media_limit)


    def send_status(self, done, type, header="", body="", extra=""):
        payload = {'done': done, 'type': type, 'header': header, 'body': body, 'extra': extra}
        socketio.emit(self._client_id, payload, namespace='/classify')


    def run(self):
        start_time = time.time()
        if not (self._algorithm or self._username):
            return

        self.send_status("false", "message", "Getting basic info on {}".format(self._username))
        try:
            userdata = collector.get_user_data(ig_client, self._username)
            time.sleep(1)
        except:
            self.send_status("true", "error", "danger", "User {} not found!".format(self._username))
            return

        if userdata["is_private"]:
            self.send_status("true", "error", "danger", "The user is private!")
            return

        self.send_status("false", "data", "User {} has {} follower(s)".format(self._username, userdata['follower_count']))

        self.send_status("false", "message", "Getting list of follower(s)")
        follower_id_list = collector.get_followers_id_list(ig_client, self._username, self._follower_limit)

        collected_comments_data = gather_comments(self._client_id, follower_id_list,
            self._media_per_follower_limit, self._comments_per_media_limit)

        self.send_status("false", "message", "Running " + self._algorithm + " algorithm")
        time.sleep(2)

        male, female = classify(self._client_id, self._algorithm, collected_comments_data)
        self.send_status("false", "data", "Male count", str(male))
        self.send_status("false", "data", "Female count", str(female))

        self.send_status("true", "message", "Done", "There are {} male(s) and {} female(s)".format(male, female),
            extra=str(self._username) + "," +
                "{0:.2f}s".format(time.time() - start_time) + "," +
                str(userdata['hd_profile_pic_url_info']['url']) + "," +
                str(male) + "," +
                str(female)
        )


def load_classifier(model_file):
    return cache.load_pickle(model_file)


def gather_comments(client_id, follower_id_list, media_per_follower_limit, comments_per_media_limit):
    total_follower = len(follower_id_list)
    client_threads[client_id].send_status("false", "data", "Targeting {} follower(s)".format(total_follower))

    collected_comments_data = []
    collected_comments_count = 0
    for follower_idx, follower in enumerate(follower_id_list):
        follower_comments = []

        all_media_id = collector.get_all_media_id(ig_client, follower, media_per_follower_limit)
        total_media = len(all_media_id)
        for media_idx, media_id in enumerate(all_media_id):
            media_comments = collector.get_media_comments(ig_client, media_id, comments_per_media_limit)

            # Filter comments that contains blacklisted words
            media_comments = [x for x in media_comments if
                all(c not in BLACKLIST_WORDS for c in x.split(' '))]

            follower_comments.extend(media_comments)

            client_threads[client_id].send_status("false", "message", "Gathering comment ",
                "follower: " + str(follower_idx) + "/" + str(total_follower) + " " +
                "media: " + str(media_idx) + "/" + str(total_media))

        if collected_comments_count + len(follower_comments) > compute_threshold:
            client_threads[client_id].send_status("false", "data", "Reached the {} compute threshold!".format(compute_threshold))
            client_threads[client_id].send_status("false", "error", "warning",
                "Reached compute threshold, stopped gathering at {} comment(s)".format(compute_threshold))

            del follower_comments[compute_threshold - collected_comments_count:]
            collected_comments_data.append(follower_comments)
            collected_comments_count += len(follower_comments)
            break
        else:
            collected_comments_data.append(follower_comments)
            collected_comments_count += len(follower_comments)

    client_threads[client_id].send_status("false", "data", "Collected comment(s)", str(collected_comments_count))
    client_threads[client_id].send_status("false", "data", "Collected follower(s)", str(total_follower))

    return collected_comments_data


def construct_follower_comments_matrix_list(follower_comments, list_of_words):
    """
    Input data is a list of list.
    Returns list of coo_matrix of every follower's comments.
    """

    total_words = len(list_of_words)
    matrix_list = []
    for comments in follower_comments:
        data = coo_matrix((1, 1))
        for c_idx, comment in enumerate(comments):
            wc = Counter()
            for word in comment.split():
                wc[word] += 1

            d = []
            for idx in range(total_words):
                count = 0
                if list_of_words[idx] in wc:
                    count = wc[list_of_words[idx]]
                d.append(count)

            if c_idx == 0:
                data = coo_matrix(d)
            else:
                data = vstack((data, coo_matrix(d)))
        matrix_list.append(data)

    return matrix_list


def classify(client_id, algorithm, data):
    """
    Input data is a list of list.
    Each sub-list contains collected comments from a particular follower.
    Returns a tuple of (male, female) followers
    """

    total_male = 0
    total_female = 0
    total_follower = len(data)
    if algorithm == "naive-bayes":
        for follower_idx, follower in enumerate(data):
            client_threads[client_id].send_status("false", "message",
                "Processing follower", " {}/{}".format(follower_idx, total_follower))

            possible_male = 0
            possible_female = 0
            for comment in follower:
                if main_classifier[algorithm](main_model[algorithm], comment) == 0:
                    possible_female += 1
                else:
                    possible_male += 1

            if possible_female > possible_male:
                total_female += 1
            else:
                total_male += 1

    elif algorithm in ["adaboost", "svm", "xgboost"]:
        matrix_data_list = construct_follower_comments_matrix_list(data, list_of_words[algorithm])
        for follower_idx, matrix_data in enumerate(matrix_data_list):
            client_threads[client_id].send_status("false", "message",
                "Processing follower", " {}/{}".format(follower_idx, total_follower))

            try:
                answer = main_classifier[algorithm](main_model[algorithm], matrix_data)
                if (answer == 0).sum() > (answer == 1).sum():
                    total_male += 1
                else:
                    total_female += 1
            except:
                continue
    else:
        client_threads[client_id].send_status("false", "error", "danger", "Invalid algorithm!")

    return total_male, total_female


@socketio.on('connect', namespace="/classify")
def connect():
    global client_threads
    client_id = request.args.get("clientID")
    client_threads[client_id] = ClientThread(client_id)

    print("[CONNECT] - " + str(client_id) + " connected")

    return client_id


@socketio.on('disconnect', namespace="/classify")
def disconnect():
    global client_threads
    client_id = request.args.get("clientID")
    print("[DISCONNECT] - " + str(client_id) + " disconnected")

    try:
        client_threads[client_id].stop()
    except:
        pass

    return client_id


@socketio.on('compute', namespace='/classify')
def compute(client_id, algorithm, username, follower_limit,
    media_per_follower_limit, comments_per_media_limit):
    global client_threads
    print("New compute request about '" + username + "' using: " +
        algorithm + " algorithm, from " + client_id)

    client_threads[client_id].setData(algorithm, username, follower_limit,
        media_per_follower_limit, comments_per_media_limit)
    client_threads[client_id].start()


@app.route('/', methods=['GET'])
def index():
    data = {'compute_threshold': compute_threshold}
    return render_template("index.html", data=data)


def main(args):
    global compute_threshold
    compute_threshold = int(os.getenv("COMPUTE_THRESHOLD", 5000))
    print("Compute threshold is set to {}".format(compute_threshold))

    global main_model
    main_model['naive-bayes'] = load_classifier('../data/model/naive_bayes_74405.p')
    main_model['svm'] = load_classifier('../data/model/svm_74420.p')
    main_model['adaboost'] = load_classifier('../data/model/ada_74420.p')
    main_model['xgboost'] = load_classifier('../data/model/xg_74420.p')

    print("Reading list of words")
    global list_of_words
    list_of_words["svm"] = cache.load_pickle("../data/model/svm_list_of_words_90670.p")
    list_of_words["adaboost"] = cache.load_pickle("../data/model/adaboost_list_of_words_90670.p")
    list_of_words["xgboost"] = cache.load_pickle("../data/model/xgboost_list_of_words_90670.p")

    global main_classifier
    main_classifier['naive-bayes'] = naive_bayes.nb_classify
    main_classifier['svm'] = svm.svm_classify
    main_classifier['adaboost'] = adab.ada_classify
    main_classifier['xgboost'] = xgb.xg_classify

    global ig_client
    ig_username = os.getenv("IG_USERNAME")
    ig_password = os.getenv("IG_PASSWORD")
    if not (ig_username or ig_password):
        print("Please set IG_USERNAME and IG_PASSWORD env variable")
        sys.exit(1)

    print("Logging into instragram account: " + ig_username)
    ig_client = ig.InstagramAPI(ig_username, ig_password)
    if not ig_client.login():
        print("Instagram login failed!")
        sys.exit(1)

    print("Reading blacklist words file")
    load_blacklist_words("../data/blacklist.txt")

    options = {
        'host': args.host,
        'port': args.port
    }
    if args.ssl_context:
        options['ssl_context'] = args.ssl_context

    app.run(**options)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        default="5001",
        help="specifies the port to listen on")

    parser.add_argument(
        "-o",
        "--host",
        action="store",
        dest="host",
        default="127.0.0.1",
        help="specifies the interface address to listen on")

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="specifies the debug mode")

    parser.add_argument(
        "-l",
        "--ssl",
        action="store",
        dest="ssl_context",
        default=None,
        help="specifies ssl_context for flask app")

    parser.add_argument(
        "-e",
        "--env",
        action="store",
        dest="env",
        default="development",
        help="specifies the env for flask to run")

    parser.add_argument(
        "-s",
        "--secret",
        action="store",
        dest="secret",
        default="",
        help="specifies the session secret key")

    args = parser.parse_args()

    app.config["ENV"] = args.env
    app.config["DEBUG"] = args.debug
    if args.secret == "":
        app.config["SECRET_KEY"] = b64encode(os.urandom(16)).decode('utf-8')
    else:
        app.config["SECRET_KEY"] = args.secret
    print("Generated secret key:", app.config["SECRET_KEY"])

    main(args)
