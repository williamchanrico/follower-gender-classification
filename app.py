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

import os
import sys
import time
from base64 import b64encode
from threading import Thread
from collections import Counter

from scipy.sparse import coo_matrix, vstack
from flask_socketio import SocketIO
from flask import Flask, render_template, request
from decouple import config

import cache
import collector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from naive_bayes import naive_bayes
from xgb import xgb
from adab import adab
from svm import svm
from thirdparty import InstagramAPI as ig

client_threads = {}
app = Flask("Instagram Follower Gender Classifier API", template_folder="./templates", static_folder="./static")
socketio = SocketIO(app)

main_model = {}
list_of_words = {}
main_classifier = {}

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
        payload = {"done": done, "type": type, "header": header, "body": body, "extra": extra}
        socketio.emit(self._client_id, payload, namespace="/classify")

    def run(self):
        start_time = time.time()
        if not (self._algorithm or self._username):
            return

        self.send_status("false", "message", "Getting basic info on {}".format(self._username))
        try:
            userdata = collector.get_user_data(ig_client, self._username)
            time.sleep(1)
        except BaseException:
            self.send_status("true", "error", "danger", "User {} not found!".format(self._username))
            return

        if userdata["is_private"]:
            self.send_status("true", "error", "danger", "The user is private!")
            return

        self.send_status("false", "data", "User {} has {} follower(s)".format(self._username, userdata["follower_count"]))

        self.send_status("false", "message", "Getting list of follower(s)")
        follower_id_list = collector.get_followers_id_list(ig_client, self._username, self._follower_limit)

        collected_comments_data = gather_comments(self._client_id, follower_id_list, self._follower_limit, self._media_per_follower_limit, self._comments_per_media_limit)

        self.send_status("false", "message", "Running " + self._algorithm + " algorithm")
        time.sleep(2)

        male, female = classify(self._client_id, self._algorithm, collected_comments_data)
        self.send_status("false", "data", "Male count", str(male))
        self.send_status("false", "data", "Female count", str(female))

        self.send_status(
            "true",
            "message",
            "Done",
            "There are {} male(s) and {} female(s)".format(male, female),
            extra=str(self._username)
            + ","
            + "{0:.2f}s".format(time.time() - start_time)
            + ","
            + str(userdata["hd_profile_pic_url_info"]["url"])
            + ","
            + str(male)
            + ","
            + str(female),
        )


def load_classifier(model_file):
    return cache.load_pickle(model_file)


def gather_comments(client_id, follower_id_list, follower_limit, media_per_follower_limit, comments_per_media_limit):
    total_follower = len(follower_id_list)
    client_threads[client_id].send_status("false", "data", "Targeting {} follower(s)".format(total_follower))

    collected_comments_data = []
    collected_comments_count = 0
    follower_count = 1
    for follower in follower_id_list:
        follower_comments = []

        all_media_id = collector.get_all_media_id(ig_client, follower, media_per_follower_limit)
        total_media = len(all_media_id)
        for media_idx, media_id in enumerate(all_media_id):
            media_comments = collector.get_media_comments(ig_client, media_id, comments_per_media_limit)

            # Filter comments that contains blacklisted words
            media_comments = [x for x in media_comments if all(c not in BLACKLIST_WORDS for c in x.split(" "))]

            follower_comments.extend(media_comments)

            client_threads[client_id].send_status(
                "false", "message", "Gathering comment ", "follower: " + str(follower_count) + "/" + str(total_follower) + " " + "media: " + str(media_idx) + "/" + str(total_media)
            )

        if len(follower_comments) > 0:
            print("No comments, skipping follower")
            follower_count += 1
        else:
            continue

        if collected_comments_count + len(follower_comments) > args["FGC_COMPUTE_THRESHOLD"]:
            client_threads[client_id].send_status("false", "data", "Reached the {} compute threshold!".format(args["FGC_COMPUTE_THRESHOLD"]))
            client_threads[client_id].send_status(
                "false", "error", "warning", "Reached compute threshold, stopped gathering at {} comment(s)".format(args["FGC_COMPUTE_THRESHOLD"])
            )

            del follower_comments[args["FGC_COMPUTE_THRESHOLD"] - collected_comments_count :]
            collected_comments_data.append(follower_comments)
            collected_comments_count += len(follower_comments)
            break
        else:
            collected_comments_data.append(follower_comments)
            collected_comments_count += len(follower_comments)

        if follower_count > follower_limit:
            break

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
            client_threads[client_id].send_status("false", "message", "Processing follower", " {}/{}".format(follower_idx, total_follower))

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
            client_threads[client_id].send_status("false", "message", "Processing follower", " {}/{}".format(follower_idx, total_follower))

            try:
                answer = main_classifier[algorithm](main_model[algorithm], matrix_data)
                if (answer == 0).sum() > (answer == 1).sum():
                    total_male += 1
                else:
                    total_female += 1
            except BaseException:
                continue
    else:
        client_threads[client_id].send_status("false", "error", "danger", "Invalid algorithm!")

    return total_male, total_female


@socketio.on("connect", namespace="/classify")
def connect():
    global client_threads
    client_id = request.args.get("clientID")
    client_threads[client_id] = ClientThread(client_id)

    print("[CONNECT] - " + str(client_id) + " connected")

    return client_id


@socketio.on("disconnect", namespace="/classify")
def disconnect():
    global client_threads
    client_id = request.args.get("clientID")
    print("[DISCONNECT] - " + str(client_id) + " disconnected")

    try:
        client_threads[client_id].stop()
    except BaseException:
        pass

    return client_id


@socketio.on("compute", namespace="/classify")
def compute(client_id, algorithm, username, follower_limit, media_per_follower_limit, comments_per_media_limit):
    global client_threads
    print("New compute request about '" + username + "' using: " + algorithm + " algorithm, from " + client_id)

    client_threads[client_id].setData(algorithm, username, follower_limit, media_per_follower_limit, comments_per_media_limit)
    client_threads[client_id].start()


@app.route("/", methods=["GET"])
def index():
    data = {"compute_threshold": args["FGC_COMPUTE_THRESHOLD"]}
    return render_template("index.html", data=data)


def main():
    print("Compute threshold is set to {}".format(args["FGC_COMPUTE_THRESHOLD"]))

    global main_model
    main_model["naive-bayes"] = load_classifier((os.path.join(args["FGC_DATA_DIR"], "model/naive_bayes_74405.p")))
    main_model["svm"] = load_classifier(str(os.path.join(args["FGC_DATA_DIR"], "model/svm_74420.p")))
    main_model["adaboost"] = load_classifier(str(os.path.join(args["FGC_DATA_DIR"], "model/ada_74420.p")))
    main_model["xgboost"] = load_classifier(str(os.path.join(args["FGC_DATA_DIR"], "model/xg_74420.p")))

    print("Reading list of words")
    global list_of_words
    list_of_words["svm"] = cache.load_pickle(str(os.path.join(args["FGC_DATA_DIR"], "model/svm_list_of_words_90670.p")))
    list_of_words["adaboost"] = cache.load_pickle(str(os.path.join(args["FGC_DATA_DIR"], "model/adaboost_list_of_words_90670.p")))
    list_of_words["xgboost"] = cache.load_pickle(str(os.path.join(args["FGC_DATA_DIR"], "model/xgboost_list_of_words_90670.p")))

    global main_classifier
    main_classifier["naive-bayes"] = naive_bayes.nb_classify
    main_classifier["svm"] = svm.svm_classify
    main_classifier["adaboost"] = adab.ada_classify
    main_classifier["xgboost"] = xgb.xg_classify

    global ig_client
    ig_username = args["FGC_IG_USERNAME"]
    ig_password = args["FGC_IG_PASSWORD"]
    if not (ig_username or ig_password):
        print("Please set FGC_IG_USERNAME and FGC_IG_PASSWORD env variable")
        sys.exit(1)

    print("Logging into instragram account: " + ig_username)
    ig_client = ig.InstagramAPI(ig_username, ig_password)
    if not ig_client.login():
        print("Instagram login failed!")
        sys.exit(1)

    print("Reading blacklist words file")
    load_blacklist_words(str(os.path.join(args["FGC_DATA_DIR"], "blacklist.txt")))

    options = {"host": args["FGC_FLASK_HTTP_LISTEN_ADDR"], "port": args["FGC_FLASK_HTTP_LISTEN_PORT"]}
    if args["FGC_FLASK_SSL_CONTEXT"] != "":
        options["ssl_context"] = args["FGC_FLASK_SSL_CONTEXT"]

    app.run(**options)


if __name__ == "__main__":
    """This is executed when run from the command line"""

    # System env variables override variables from .env file
    args = {
        "FGC_IG_USERNAME": config("FGC_IG_USERNAME", default=""),
        "FGC_IG_PASSWORD": config("FGC_IG_PASSWORD", default=""),
        "FGC_FLASK_ENV": config("FGC_FLASK_ENV", default="development"),
        "FGC_FLASK_DEBUG": config("FGC_FLASK_DEBUG", default=""),
        "FGC_FLASK_HTTP_LISTEN_ADDR": config("FGC_FLASK_HTTP_LISTEN_ADDR", default="localhost"),
        "FGC_FLASK_HTTP_LISTEN_PORT": config("FGC_FLASK_HTTP_LISTEN_PORT", default="9000"),
        "FGC_FLASK_SESSION_SECRET": config("FGC_FLASK_SESSION_SECRET", default=""),
        "FGC_FLASK_SSL_CONTEXT": config("FGC_FLASK_SSL_CONTEXT", default=""),
        "FGC_COMPUTE_THRESHOLD": config("FGC_COMPUTE_THRESHOLD", default=5000, cast=int),
        "FGC_DATA_DIR": config("FGC_DATA_DIR", default="data"),
    }

    app.config["ENV"] = args["FGC_FLASK_ENV"]
    app.config["DEBUG"] = args["FGC_FLASK_DEBUG"]
    if args["FGC_FLASK_SESSION_SECRET"] == "":
        app.config["FGC_FLASK_SESSION_SECRET_KEY"] = b64encode(os.urandom(16)).decode("utf-8")
        print("Generated secret key:", app.config["FGC_FLASK_SESSION_SECRET_KEY"])
    else:
        app.config["FGC_FLASK_SESSION_SECRET_KEY"] = args["FGC_FLASK_SESSION_SECRET"]

    main()
